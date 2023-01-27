#!/usr/bin/env python

# These imports should be cut down to what is needed.
import h5py
import numpy as np
import sys
from os.path import exists
from os.path import *
from struct import unpack
import matplotlib.pyplot as plt

class Spectrum():

    def __init__(self, spec, *args, **kwargs): 
        """
        spec should be individual dataset read in by h5py.File
        Then the spectrum comes out as an array and the attributes as a dictionary
        """                   
        self.spec = spec                                                                              
        self.hdr =  spec.attrs                 
        self._calc_inten_unc_per_1000()


    def _calc_inten_unc_per_1000(self):              # Belongs in Spectrum class
        try: 
            if self.hdr['intencalunc'] == 0 :
                print("Intensity calibration uncertainty is zero in header - using a default of 0.07 for calibration uncertainty")
                self.hdr['intencalunc'] = 0.07
        except:
            print("Intensity calibration uncertainty is zero in header - using a default of 0.07 for calibration uncertainty")
            self.hdr['intencalunc'] = 0.07
        
        print("Calculating uncertainty of calibration between ", self.hdr['bandlo'], " and ", self.hdr['bandhi'])
        self.hdr['calunc_per_1000']=1000*self.hdr['intencalunc']/(float(self.hdr['bandhi'])-float(self.hdr['bandlo']))
    
        return()

class LineSpec():
    """ 
    This describes one line in the intensity corrected linelist.
    In the example file Cr_BF2.h5, if the file is opened with h5py.File, the linelist
    is read out as a list of dictionaries (I think).
    """
    def __init__(self,line,spectrum, *args, **kwargs):
        self.sig = line['sig']
        self.xint = line['xint']
        self.width = line['width']        # Should we convert this to cm-1 (i.e. divide by 1000?)
        self.dmping = line['dmping'] 
        self.ew = line['ew']

        self.npts = 0.001*self.width/float(spectrum.hdr['resolutn'] )   # no. points/FWHM.
        """ 
        Following line is equation 9 of Sikstrom (2002) with alpha_sigma = 0.8. Values
        should be 0.69 for Gaussian, 0.8 for Lorentzian, so this is slightly pessimistic.
        Note that Davis, Abrams & Brault assumed alpha_sigma = 1 in equation 9.3 
        """
        self.sig_statunc = 0.8 * 0.001*self.width/(np.sqrt(self.npts) * self.xint)   

        """  
        From eqn 3 of Ward et al. 2023 (Cr II BF paper) with alpha_y = 1.5.
        This is the statistical uncertainty of the line. The total uncertainty
        of the branching fraction must be calculated in the target_level class
        as it requires us to know the distance of the line from the strongest decay.
        """
        self.inten_unc = np.sqrt(2.25/(self.xint**2 * self.npts )   )  


class EnergyLevel():
    """
    Now modified to use a level list with keys in the hdf5 file
    """
    def __init__(self,lev_list,*args,**kwargs):
        self.desig = lev_list['desig']
        self.J = float(lev_list['J'])
        self.energy = float(lev_list['energy'])
        self.parity = lev_list['parity'] 
        self.lifetime = lev_list['lifetime']
        self.key = lev_list['key']
        self.species = lev_list['species']
        self.uncertainty = float(lev_list['uncertainty'])

    def _lev_with_lifetime(self, *args, **kwargs):
        """ 
        Return all the levels with non-zero lifetimes
        """

        life_lev = [i for i in self if i.lifetime !=b'-']
        return(life_lev)

        
class target_level:
    level = EnergyLevel  

    calculations =str           # ?? array? list of tuples? 
    expt_data    =str           # will contain snr and inten for each lower level and spectrum. How to arrange?
    results       =str           # ???
    w_maxI       =str            # Wavenumber of strongest line in branch in each spectrum. A dictionary of floats?

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
                    self.w_maxI = i.sig           # Check indexing of this - not sure it will work.
        return()
       
# class calculations():

#     def __init__(self,calc_list, *args, **kwargs):
#         """ 
#         Contains calculated log(gf) values from e.g. Kurucz, Raassen & Uylings
#         """
        


# def match_calcs(linelist, calcs):
