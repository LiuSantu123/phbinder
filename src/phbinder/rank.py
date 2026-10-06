import pandas as pd
import numpy as np

def percentile(s, higher=True):
    x=pd.to_numeric(s, errors="coerce"); r=x.rank(pct=True).fillna(0.0)
    return r if higher else 1-r

def rank_frame(df, weights):
    d=df.copy()
    def col(name, default=0.0): return d[name] if name in d else pd.Series(default,index=d.index)
    d["structure_score"]=0.6*percentile(col("interface_atom_contacts"))+0.4*percentile(col("interface_binder_residues"))
    d["ph_score"]=0.7*percentile(col("delta_electrostatic_energy").abs())+0.3*percentile(col("interface_switchable"))
    d["combined_score"]=(weights.get("structure_confidence",.3)*d.structure_score+
        weights.get("electrostatic_delta",.25)*d.ph_score+
        weights.get("interface_titratable",.2)*percentile(col("interface_titratable_binder"))+
        weights.get("interface_energy",.15)*percentile(col("interface_energy"),False)+
        weights.get("dynamics",.1)*percentile(col("dynamics_score")))
    return d.sort_values("combined_score",ascending=False).reset_index(drop=True)
