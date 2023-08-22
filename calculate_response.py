
"""
Dataframes:

 2) standard_lamp_spectra:
      Wavenumber

      Interpolated calibration certificate

      Intensity from before spectrum
      Intensity from after spectrum
      Other spectra ...

      Filtered version of before spectrum
      Filtered version of after spectrum
      Filtered version of other spectra ...

      Average filtered spectrum
      Response curve 

"""


def CalculateResponse(standard_lamp_spectra):

    """
    Save the response curve generated from the interpolated standard lamp spectrum
    and the filtered, averaged spectra as another column in the dataset
    """

    """
    Check that all spectra are on same wavenumber scale
    """





    standard_lamp_spectrum['response'] = standard_lamp_spectra['average']/standard_lamp_spectra['interpolated_certificate']

    return()



def AverageSpectra(standard_lamp_spectra):

    return()




def FilterSpectrum(spectrum, filter, width):
    
    """
    Two possible filters can be applied. The first is a boxcar used to match a spectrometer used to
    produce the calibration certificate. This might be applied twice, for an entrance and exit slit.
    e.g. the PTB spectrometer can be matched with slits of roughly 0.92 nm and 0.46 nm. This filter would
    have to be applied in wavelength space, not wavenumber space.

    The second filter is a Gaussian filter used to smooth over the noise. The width would be specified
    in wavenumbers.
    """


    return()

standar