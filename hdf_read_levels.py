import h5py
from branching_fraction import EnergyLevel

""" 
Test program to read energy levels from hdf5 file
"""

with h5py.File('Cr_BF2.h5', 'r') as f:
    levels = f['Levels/Cr II levels']
    print(levels[0]['desig'])              

    # Convert levels from a list of dictionaries to a list of EnergyLevel objects

    levs = [EnergyLevel(level) for level in levels]
    for i in range(0,5):
        print (levs[i].energy, levs[i].J)  
        
    # Find all the levels with non-zero lifetimes

    n=0
    lev_with_lifetime = [i for i in levs if i.lifetime !=b'-']
    for i in lev_with_lifetime:
        print(i.desig, i.energy , i.uncertainty,  i.J, float(i.lifetime))  
        n = n+1

    print(n, " levels with lifetimes")
        
           
