import h5py
from branching_fraction import EnergyLevel, Spectrum


""" 
Test program to read energy levels from hdf5 file
"""

def getlevs():
    with h5py.File('Cr_BF2.h5', 'r') as f: 
        levels = f['Levels/Cr II levels']
        
        # Convert levels from a list of dictionaries to a list of EnergyLevel objects

        levs = [EnergyLevel(level) for level in levels]

    life_lev = EnergyLevel._lev_with_lifetime(levs)
    n=0
    for i in life_lev:
        print(i.desig, i.energy , i.uncertainty,  i.J, float(i.lifetime))
        n = n+1

    print(n, "levels with lifetimes")

    return()

def getspec(fname):
    with h5py.File(fname,'r+') as f:
        spec = Spectrum( f['Spectra/Cr110600.001/spectrum/spectrum'] )

        print(spec.hdr['calunc_per_1000'])
    
    return()

getspec('Cr_BF2.h5')
