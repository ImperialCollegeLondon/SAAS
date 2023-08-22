"""
Dataframes:

 1) calibration_certificate:
      Wavelength
      Original radiance columns (maybe multiple columns as from original certificate)
      Radiance in photons/cm-1
 
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

from scipy.interpolate import interp 
import matplotlib.pyplot as plt

from WavenumberConversions import airtovac

def InterpolateCalibration(calibration_certificate, wstart, wstop, delw):
    
    """ 
       Calibration certificate is a dataframe with wavelength(nm), intensity(W per cm^-2.sr.nm).
       This should be converted to photons per wavenumber and saved in additional column.
       wstart should be first wavenumber in the measured spectrum and wstop the last
       delw is the desired interpolation in wavenumbers. Should be the same as the measured spectrum
    """
    if calibration_certificate has no column for photons per wavenumber:

      calibration_certificate['PhotonsPerWavenumber'] = ConvertToPhotonsPerWavenumber(calibration_certificate)

    """
       Cubic spline interpolation should be used. First define the grid for the interpolation
       Try using interpn for cubic interpolation
    """

    xi = np.linspace(wstart, wstop, num=(wstart-wstop)/delw+1)  
    """
    Check that number of points is correct. 
    """

    standard_lamp_spectra['interpolated_certificate'] = interp(calibration_certificate, xi, method='cubic')

    PlotInterpolatedCalibration(calibration_certificate['PhotonsPerWavenumber'],(xi,interpolated_calibration))

    if(plot not OK ):
       # Need to change some parameters if it doesn't look right
       # Question is what and how.

    """
    Save the result to HDF file in Spectra->Spectrum n -> Spectra of calibration lamp -> Interpolated standard lamp calibration
    """

    location = ("Spectra->Spectrum n -> Spectra of calibration lamp -> Interpolated standard lamp calibration")

    WriteToHDF(location,interpolated_calibration)   # Save the result somewhere in the HDF5 file

    return((xi,interpolated_calibration))     # Return interpolated calibration in additional column
    

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

def PlotInterpolatedCalibration(converted_certificate,(xi,interpolated_calibration)):
    
    """
    Plot the interpolated calibration on top of the original data. Verify it's OK
    Where do we put the plot?
    """

    plt.plot(converted_certificate,label="Original data")     
    """
    converted certificate is a tuple. Make the original data a scatter plot
    """
    plt.plot(xi,interpolated_calibration,label="Interpolated data")  # Make this a line plot
    plt.xlabel("Wavenumber (cm-1)")
    plt.ylabel("Radiance (photons/(cm-1.cm^2.sr)")  # Scale units if necessary
    plt.title("Interpolated radiance")y/n

    message("OK y/n ")

    return()



