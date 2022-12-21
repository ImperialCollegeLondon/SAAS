#!/usr/bin/env python

from tables import *
import h5py
import numpy as np
import sys
from os.path import exists
from os.path import *
from struct import unpack
import matplotlib.pyplot as plt


class spectrum():

    def __init__(self, spec, *args, **kwargs): 
        """
        spec should be individual dataset read in by h5py.File
        Then the spectrum comes out as an array and the attributes as a dictionary
        """                   
        self.spec = spec                                                                              
        self.hdr =  spec.attrs                 
        self._calc_inten_unc_per_1000()
        return()

    def _calc_inten_unc_per_1000(self):              # Belongs in spectrum class
        if self.hdr['intencalunc'] == 0:
            print("Intensity calibration uncertainty is zero - please change in the hdf5 file")
            return(-1)
        else:
            print(f 'Calculating uncertainty of calibration between ' {self.hdr['bandlo']:> 6.0f} and {self.hdr['bandhi']:>6.0f})
            self.calunc_per_1000=spectrum.hdr['intencalunc']/(self.hdr['bandhi']-self.hdr['bandlo'])
    
        return()


class LineSpec(IsDescription):
    sig = Float64Col()
    xint = Float32Col()
    width = Float32Col()
    dmping = Float32Col()
    ew = Float32Col()
    itn = Int16Col()
    ihold = Int16Col()
    tags = StringCol(4)
    epstot = Float32Col()
    epsevn = Float32Col()
    epsodd = Float32Col()
    epsran = Float32Col()
    spare = Float32Col()
    ident = StringCol(32)

    def __init__(self,row):
        self.sig = row[0]                         # example to expand
        self.xinit = row[0]                      

        self.npts=0.001*self.width/spectrum.hdr['resoln']    # no. points/FWHM.
        self.inten_unc=2.25/(self.xinit**2 * self.npts )     # From eqn 3 of Ward et al. 2023 (Cr II BF paper) with alpha_y = 1.5

    def _calc_inten_unc(self,spectrum):
        return()


class target_level:
    ident = str             # a string
    j_val = float           # a number (float)
    level_value = float     # a number (float)
    parity  = str           # a string (? odd, even; or 0 and 1?)
    lifetime = float        # a number (float)
    key    = str            # a string
    calculations            # ?? array? list of tuples? 
    expt_data               # will contain snr and inten for each lower level and spectrum. How to arrange?
    results                 # ???
    w_maxI                  # Wavenumber of strongest line in branch in each spectrum. A dictionary of floats?

    def __init__(self):
        return()

    def _strongest_line(self,line):       #
        
        """
        Description:
            Finds the wavenumber of the strongest line in the branch in this spectrum
            Used in the calculation of the calibration uncertainty
        """

        for j in self.expt_data.spectrum:
            for i in self.expt_data:
                if float(j.i.xint)> maxI :        # Find the wavenumber of the strongest line
                    maxI = i.xint                 # Used for calibration uncertainty
                    self.w_maxI = line.sig
        return()


      """
      Code from Christian 
      """  

class EnergyLevel():
    def __init__(self,lev_list,*args,**kwargs):
        self.desig = lev_list[0]
        self.J = lev+list[1]

levs = [EnergyLevel(level) for level in levels]
print(lev)