from phbinder.external import PDB2PQRAdapter, APBSAdapter, RosettaInterfaceAdapter, MMPBSAAdapter

def test_command_builders():
    p=PDB2PQRAdapter('/bin/pdb2pqr')
    assert p.command('x.pdb','x.pqr', 'x.in', 6.5)[-2:] == ['x.pdb','x.pqr']
    assert APBSAdapter('/bin/apbs').command('x.in')[-1]=='x.in'
    assert '-s' in RosettaInterfaceAdapter('/bin/rosetta').command('x.pdb','score.sc')
    assert '-cp' in MMPBSAAdapter('/bin/mmpbsa').command('m.in','c.prmtop','o.dat')
