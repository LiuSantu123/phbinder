from pathlib import Path
import re
import numpy as np

TITRATABLE = {"ASP": "acid", "GLU": "acid", "CYS": "acid", "TYR": "acid",
              "HIS": "base", "LYS": "base", "ARG": "base"}

def _pdb_atoms(path: Path):
    atoms=[]
    for line in path.read_text(errors="ignore").splitlines():
        if not line.startswith(("ATOM", "HETATM")): continue
        try:
            atoms.append({"chain": line[21].strip() or "_", "resno": int(line[22:26]),
                "resname": line[17:20].strip(), "xyz": np.array([float(line[30:38]),float(line[38:46]),float(line[46:54])])})
        except (ValueError, IndexError): pass
    return atoms

def atoms(path: str | Path):
    path=Path(path)
    if path.suffix.lower()==".pdb": return _pdb_atoms(path)
    try:
        from biotite.structure.io.pdbx import CIFFile, get_structure
        a=get_structure(CIFFile.read(path), model=1)
        return [{"chain": str(a.chain_id[i]), "resno": int(a.res_id[i]),
                 "resname": str(a.res_name[i]), "xyz": np.asarray(a.coord[i])} for i in range(len(a))]
    except Exception as e:
        raise RuntimeError(f"Cannot parse {path}; install biotite for CIF input: {e}")

def interface_stats(path, target="A", binder="B", cutoff=8.0):
    aa=atoms(path); ta=[x for x in aa if x["chain"]==target]; ba=[x for x in aa if x["chain"]==binder]
    if not ta or not ba: raise ValueError(f"missing target/binder chain ({target}/{binder})")
    x=np.array([a["xyz"] for a in ta]); y=np.array([a["xyz"] for a in ba])
    d=np.linalg.norm(x[:,None,:]-y[None,:,:],axis=2)
    ti={ (a["resno"],a["resname"]) for i,a in enumerate(ta) if np.any(d[i]<=cutoff)}
    bi={ (a["resno"],a["resname"]) for j,a in enumerate(ba) if np.any(d[:,j]<=cutoff)}
    return {"interface_atom_contacts": int(np.sum(d<=cutoff)),
            "interface_target_residues": len(ti), "interface_binder_residues": len(bi),
            "interface_titratable_target": sum(r in TITRATABLE for _,r in ti),
            "interface_titratable_binder": sum(r in TITRATABLE for _,r in bi),
            "interface_residues_target": sorted(f"{r}{n}" for n,r in ti),
            "interface_residues_binder": sorted(f"{r}{n}" for n,r in bi)}

def heuristic_ph_delta(stats):
    # A screening prior only; it is replaced by APBS when configured.
    n=stats["interface_titratable_target"]+stats["interface_titratable_binder"]
    return float(n), "heuristic_interface_titratable_prior"
