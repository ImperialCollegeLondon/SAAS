from scipy.interpolate import interp 
from WavenumberConversions import airtovac

def InterpolateCalibration(calibration_certificate, wstart, wstop, delw):
    
    """ 
       Calibration certificate is a tuple of wavelength(nm), intensity(W per cm^-2.sr.nm)
       wstart should be first wavenumber in the measured spectrum and wstop the last
       delw is the desired interpolation in wavenumbers. Should be the same as the measured spectrum
    """

    converted_certificate = ConvertToPhotonsPerWavenumber(calibration_certificate)

    waveno = np.linspace()    # Define new wavenumber scale for calibration
  
    """
       Cubic spline interpolation should be used. First define the grid for the interpolation
       Try using interpn for cubic interpolation
    """

    xi = np.linspace(wstart, wstop, num=(wstart-wstop)/delw+1)  

    interpolated_calibration = interpolate.interpn(converted_certificate, xi, method='cubic')

    return((xi,interpolated_calibration))     # Return a tuple of the interpolated calibration
    

def ConvertToPhotonsPerWavenumber(calibration_certificate):
    """
       Need to convert wavelengths to wavenumbers
       Original data in W per cm^-2.sr.nm. We need to convert to photons/nm
       Presume original data has air wavelengths above 200 nm.
       So need to multiply intensities by wavelength^3   
       Do we need to be careful around 200 nm ??
    """
    wavenumbers = airtovac(calibration_certificate[0])

    sort_in_wavenumber_order(wavenumbers,calibration_certificate[1])

    converted_certificate = calibration_certificate[1]/(wavenumbers^3)

    return((wavenumbers,converted_certificate))
