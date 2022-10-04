#
# The classes and methods we need to describe our data and work on it.
#

class Line:
    wavenumber      # Wavenumber measured in the spectrum or averaged in cm-1.
    SNR             # Signal-to-noise ratio (Peak in Xgremlin)
    FWHM            # Full Width at Half Maximum in 0.001 cm-1
    damping         # Damping parameter of the Voigt profile
    intensity       # Integrated intensity (EW in Xgremlin)
    wavelength      # Air wavelength in nm. Can be calculated from other params
    waveno_unc      # Wavenumber uncertainty. Can be calculated from other
                    # params if the 'spectrum' class is inherited
    keff            # Wavenumber calibration constant keff.
                    # Could be inherited from 'spectrum' class.

    def vac_to_air  # Convert vacuum wavenumbers to air wavelength

    def stat_unc    # Calculate the statistical uncertainty of the wavenumbers

    def total_unc   # Calculate the total uncertainty of the wavenumber,
                    # including the calibration uncertainty and the uncertainty
                    # of the reference wavenumbers

    def calib_waveno # Calibrate the wavenumbers and wavelengths using keff from
                    # the 'spectrum' classes

    def calib_intensity # Calibrate the integrated intensity from the response
                    # function in the 'spectrum' class

class Spectrum:     # A class to describe the experimental data
    <header values> # All of the values from old .hdr files: wstart, delw, nop ...
                    # This would include keff (wavcorr in the header).
    data            # All of the data from the old .dat files
    response        # Response function calculated from spectra taken at same time

    def read_spectrum # A function to either read the old .hdr and .dat files,
                    # or to read in the hdf5 file. If it reads old style files
                    # it should convert the to hdf5, unless there is an existing
                    # hdf5 file, in which case it should ask what to do.

    def write_hdf5  # A function to write everything out to a new hdf5 files

    def add_to_hdf5 # A function to add something to a hdf5 file. e.g. to add
                    # a new linelist from a new analysis.

    def calc_keff   # Calculate the wavenumber correction factor keff from a
                    # set of reference lines. Should include a plot of the
                    # residuals and a calculation of the weighted mean.
                    # Should be an ability to delete points for the mean.
                    # Could be adapted from Christian's ftscalib.py

    def plot_spectrum # Plot a portion of the spectrum between two wavenumbers.

class EnergyLevel:
    species         # The atom and ionization stage (e.g. FeII)
    key             # Some common key to link all the levels from the various
                    # sources together? Is there a better way of doing this?
    config          # Configuration
    term            # Term in appropriate coupling scheme
    J_value         # J value of the level
    parity          # odd or even parity
    level_value     # The energy of the level in cm-1
    level_unc       # The uncertainty of the level in cm-1
    HFS_A           # Hyperfine structure parameter A in 0.001 cm-1
    HFS_B           # Hyperfine structure parameter B in 0.001 cm-1

    def level_match # Match the energy levels from two or more different sources,
                    # e.g. ASD, Kurucz, or Raassen

    def read_levels # Read in a set of energy levels from some source (ASD etc.)

class Transition:
    lower_level     # Lower level of transition, from the class 'EnergyLevel'
    upper_level     # Upper level of transition, from the class 'EnergyLevel'
    ritz_waveno     # Ritz wavenumber of transition in cm-1, derived from
                    # Values of upper and lower levels.
    ritz_waveno_unc # Uncertainty. This comes from the LOPT output.

    def calc_ritz_waveno   # Calculate the Ritz wavenumber and uncertainty
                    # from the upper and lower levels.


class Linelist:
                    # Linelists can be for a single spectrum, or
                    # could be an average of several spectra.
    line            # The observed lines, of class Line
    transition      # The identifications, of class transition
                    # Lines may have more than one transition, or none.
    def read_lines  # Read in existing linelist. Only from legacy file, if
                    # hdf5 linelist read automatically?
    def remove_id   # Remove the identification from a line. Keep it in a
                    # separate list of deleted lines (group and datatype in hdf5).
    def add_ids     # Add identifications from a separate list of id'd lines.

    def match_ritz  # Match the wavenumbers to Ritz wavenumbers from the class
                    # 'Transition'. Like the old 'strans'.
    def average_lists # Create an averaged linelist from a set of other linelists.
                    # These may or may not contain identifications, but if they
                    # do the function must have some way to decide what's correct.
                    # There should be traceability so that you can figure out
                    # what's been averaged to create each value.

    def level_opt   # optimize the energy levels to the linelist using LOPT.

    def level_search # Search for new energy levels using linelist and subset
                    # of existing levels.
