import numpy as np

def calc_stat_unc(fwhm, res, snr): 
    """
    Calculates the statistical uncertainty of a voigt fitted spectral line. Formula from: Craig J. Sansonetti and Gillian Nave 2014 ApJS 213 28.
    
    Inputs:
    fwhm: full width at half maximum of the line (in mK)
    res: resolution of the spectrum
    snr: signal to noise ratio of the spectral line
    """ 
    
    fwhm = fwhm / 1000  # convert from mK (Xgremlin standard output) to cm-1

    return np.sqrt(fwhm * res) / snr  # Same as: FWHM / (np.sqrt(Number of independant points across FWHM) * SNR)