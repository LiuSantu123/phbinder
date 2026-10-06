from pathlib import Path
from phbinder.structure import interface_stats

def test_interface_stats(tmp_path: Path):
    p=tmp_path/'x.pdb'
    def line(i,atom,res,chain,n,x,y,z):
        return f"ATOM  {i:5d} {atom:<4} {res:>3} {chain}{n:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00 20.00           C\n"
    p.write_text(line(1,'CA','ASP','A',1,0,0,0)+line(2,'CA','HIS','B',1,0,0,6)+"END\n")
    x=interface_stats(p)
    assert x['interface_atom_contacts']==1
    assert x['interface_titratable_target']==1
    assert x['interface_titratable_binder']==1
