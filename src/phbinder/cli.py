import argparse, csv, json, os, sys, hashlib, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pandas as pd
import yaml
from .model import Candidate, Result, write_json
from .structure import interface_stats, heuristic_ph_delta
from .rank import rank_frame
from .tools import executable, run
from .external import ensure_pdb, propka, apbs_pair

def cfg(path):
    d=yaml.safe_load(Path(path).read_text()) if path else {}
    def expand(x):
        if isinstance(x,str):
            return re.sub(r"\$\{([^}:]+)(?::-([^}]*))?\}",lambda m:os.environ.get(m.group(1),m.group(2) or ""),x)
        if isinstance(x,dict): return {k:expand(v) for k,v in x.items()}
        return x
    d=expand(d)
    d.setdefault("ph_on",6.5); d.setdefault("ph_off",7.4); d.setdefault("workers",4); d.setdefault("mode","standard")
    d.setdefault("chains",{}); d.setdefault("tools",{}); d.setdefault("weights",{})
    d["chains"].setdefault("target","A"); d["chains"].setdefault("binder","B")
    return d

def candidates(input_dir, c):
    root=Path(input_dir); out=[]
    for p in sorted(root.rglob("*")):
        if p.suffix.lower() not in {".pdb",".cif"}: continue
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        cid=f"{p.stem}__{h[:10]}"
        out.append(Candidate(cid,str(p),c["chains"]["target"],c["chains"]["binder"],h))
    if not out: raise SystemExit(f"No .pdb/.cif structures found in {root}")
    return out

def one(c, out, config, force=False, cache=True):
    propka_exe=executable(config['tools'].get('propka'),'propka3')
    od=Path(out)/"per_design"/c.candidate_id
    if cache or propka_exe: od.mkdir(parents=True,exist_ok=True)
    jp=od/"metrics.json"
    if cache and jp.exists() and not force: return json.loads(jp.read_text())
    try:
        v=interface_stats(c.structure,c.target_chain,c.binder_chain,float(config.get("interface_cutoff_angstrom",8.0)))
        n,method=heuristic_ph_delta(v)
        pk={'method':'unavailable','ionizable':0,'switchable':0,'delta_charge':0.0}
        if propka_exe:
            pdb=ensure_pdb(c.structure, od/(c.candidate_id+'.pdb'))
            pk=propka(pdb, od/'propka', propka_exe, config['ph_on'], config['ph_off'])
        apbs_data=None
        p2q=executable(config['tools'].get('pdb2pqr'),'pdb2pqr'); apbs=executable(config['tools'].get('apbs'),'apbs')
        if p2q and apbs:
            if 'pdb' not in locals(): pdb=ensure_pdb(c.structure, od/(c.candidate_id+'.pdb'))
            apbs_data=apbs_pair(pdb,od/'apbs',p2q,apbs,config['ph_on'],config['ph_off'])
        v.update({"candidate_id":c.candidate_id,"structure":c.structure,"input_sha256":c.input_sha256,"status":"complete",
                  "pH_on":config["ph_on"],"pH_off":config["ph_off"],
                  "delta_electrostatic_energy":apbs_data['delta'] if apbs_data else (pk['delta_charge'] if pk['method']=='propka' else n),
                  "interface_switchable":pk['switchable'] if pk['method']=='propka' else n,
                  "propka_ionizable":pk['ionizable'],"ph_method":pk['method'] if pk['method']!='unavailable' else method,
                  "mode":config["mode"],
                  "apbs_energy_on":apbs_data[str(config['ph_on'])] if apbs_data else None,
                  "apbs_energy_off":apbs_data[str(config['ph_off'])] if apbs_data else None,
                  "apbs_status":"complete" if apbs_data else "not_run"})
        # External integrations are opt-in. Keep the result usable when a tool is absent.
        v["external_tools_available"]={k:bool(executable(x, k)) for k,x in config["tools"].items()}
        if cache: write_json(jp,v)
        return v
    except Exception as e:
        v={"candidate_id":c.candidate_id,"structure":c.structure,"status":"failed","error":str(e)}
        if cache: write_json(jp,v)
        return v

def screen(args):
    c=cfg(args.config); cs=candidates(args.input,c)
    csv_out=Path(args.output) if getattr(args,'output',None) else None
    out=Path(args.out) if getattr(args,'out',None) else (csv_out.parent if csv_out else Path('phscreen_results'))
    out.mkdir(parents=True,exist_ok=True)
    if args.ph_on is not None: c["ph_on"]=args.ph_on
    if args.ph_off is not None: c["ph_off"]=args.ph_off
    results=[]
    with ThreadPoolExecutor(max_workers=args.workers or c["workers"]) as ex:
        fs=[ex.submit(one,x,out,c,args.force,not csv_out) for x in cs]
        for i,f in enumerate(as_completed(fs),1):
            results.append(f.result()); print(f"screened {i}/{len(cs)}",flush=True)
    fields=sorted({k for x in results for k in x if not isinstance(x[k],(list,dict))})
    metrics_path=csv_out or (out/"metrics.csv")
    if csv_out:
        # Direct mode is the user-facing path: emit the ranked CSV, not an
        # unscored intermediate table.
        ranked=rank_frame(pd.DataFrame(results),c["weights"])
        ranked.to_csv(metrics_path,index=False)
    else:
        with metrics_path.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows([{k:x.get(k) for k in fields} for x in results])
    if not csv_out:
        write_json(out/"run_metadata.json",{"config":c,"n_input":len(cs),"n_complete":sum(x.get("status")=="complete" for x in results)})
    print(f"wrote {metrics_path} ({sum(x.get('status')=='complete' for x in results)}/{len(results)} complete)")

def rank(args):
    c=cfg(args.config); d=pd.read_csv(args.metrics); d=d[d.status.eq("complete")].copy()
    d=rank_frame(d,c["weights"]); Path(args.out).parent.mkdir(parents=True,exist_ok=True); d.to_csv(args.out,index=False)
    if args.top:
        d.head(args.top).to_csv(Path(args.out).with_name(Path(args.out).stem+f"_top{args.top}.csv"),index=False)
    print(f"ranked {len(d)} candidates")

def doctor(args):
    c=cfg(args.config); print('phbinder tool check')
    for name,path in c['tools'].items():
        exe=executable(path,name)
        print(f"{name}: {exe or 'NOT FOUND'}")
    print(f"pH on/off: {c['ph_on']} / {c['ph_off']}")
    print(f"chains: target={c['chains']['target']} binder={c['chains']['binder']}")

def main():
    if len(sys.argv)>1 and sys.argv[1] not in {"screen","rank","run","doctor","-h","--help"}: sys.argv.insert(1,"screen")
    p=argparse.ArgumentParser(prog="phbinder"); sub=p.add_subparsers(dest="command",required=True)
    s=sub.add_parser("screen"); s.add_argument("--input",required=True); s.add_argument("--output"); s.add_argument("--out"); s.add_argument("--config",default=None); s.add_argument("--workers",type=int); s.add_argument("--ph-on",type=float); s.add_argument("--ph-off",type=float); s.add_argument("--force",action="store_true"); s.set_defaults(func=screen)
    r=sub.add_parser("rank"); r.add_argument("--metrics",required=True); r.add_argument("--out",required=True); r.add_argument("--config",required=True); r.add_argument("--top",type=int,default=20); r.set_defaults(func=rank)
    d=sub.add_parser("doctor"); d.add_argument("--config",default=None); d.set_defaults(func=doctor)
    a=sub.add_parser("run"); a.add_argument("--input",required=True); a.add_argument("--out",required=True); a.add_argument("--config",required=True); a.add_argument("--workers",type=int); a.add_argument("--ph-on",type=float); a.add_argument("--ph-off",type=float); a.add_argument("--top",type=int,default=20); a.add_argument("--force",action="store_true")
    args=p.parse_args()
    if args.command=="run":
        screen(args); args.metrics=str(Path(args.out)/"metrics.csv"); args.out=str(Path(args.out)/"ranked.csv"); args.command="rank"; args.func=rank
    args.func(args)
