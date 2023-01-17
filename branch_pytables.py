""" These classes are the descriptors for the hdf5 file tables to be generated from user selected starting files"""

import tables as tb
import numpy as np

class EnergyTable(tb.IsDescription):
    """Descriptor for energy level data table"""
    desig = tb.StringCol(32)
    j = tb.Float16Col()
    energy = tb.Float32Col()
    energy_unc = tb.Float32Col()
    parity = tb.UInt8Col()
    species = tb.StringCol(8)
    lifetime = tb.Float32Col()
    lifetime_unc = tb.Float32Col()
    
    
class CalculationTable(tb.IsDescription):
    """Descriptor for calcluated lines table"""
    lower_desig = tb.StringCol(32)
    upper_desig = tb.StringCol(32)
    log_gf = tb.Float32Col()
    
    
class PreviousLinesTable(tb.IsDescription):
    """Descriptor for the previously observed line table"""
    wavenumber = tb.Float32Col()
    lower_energy = tb.Float32Col()
    upper_energy = tb.Float32Col()
    lower_desig = tb.StringCol(32)
    upper_desig = tb.StringCol(32)
    snr = tb.Float32Col()
    intensity = tb.Float32Col()
    note = tb.StringCol(64)
    
    
class SprectumTable(tb.IsDescription):
    """Descriptor for Spectrum .dat table. The .hdr data will all be stored at attributes (attrs) of this table"""
    wavenumber = tb.Float32Col()
    snr = tb.Float32Col()
    
    
class LinelistTable(tb.IsDescription):
    """Descriptor for the linelist file associated with a spectrum. Wavenumber, air and intensity correction will be stored as attributes of this table"""
    line_num = tb.UInt16Col()
    wavenumber = tb.Float32Col()
    snr = tb.Float32Col()
    width = tb.Float32Col()  # in mK (10^-3 cm-1)
    damping = tb.Float32Col()
    eq_width = tb.Float32Col()
    tags = tb.StringCol(8)
    

fileh = tb.open_file('test.h5', 'w')

levels_group = fileh.create_group(fileh.root, 'levels', 'Levels')
spectra_group = fileh.create_group(fileh.root, 'spectra', 'Spectra')
previous_lines_group = fileh.create_group(fileh.root, 'previousLines', 'Previous Lines')
calculations_group = fileh.create_group(fileh.root, 'calculations', 'Calculations')

hdr_file = 'test.hdr'
dat_file = 'test.dat'
lin_file = 'test.cln'

def create_spectrum_table(hdf5file, group, dat_file, hdr_file):
    spectrum_group = hdf5file.create_group(group, dat_file[:-4], dat_file[:-4])  # create the group for the spectra
    table = hdf5file.create_table(spectrum_group, dat_file[:-4], SprectumTable, dat_file)  # create table for .dat file

    # Set attributes of the .dat table as the parameters of the .hdr file
    with open(hdr_file, 'r') as f:
        hdr_lines = f.readlines()
        
        for line in hdr_lines:
            if '=' in line:  # is a parameter line
                line_parts = line.split('=')
                parameter = line_parts[0].strip()  # parameter name
                
                if parameter == 'continue':  # because 'continue' is a reserved Python keyword
                    parameter = 'continue_'
                
                value = line_parts[1].split('/ ')[0].replace("'","").strip()  
                
                try:  # set any parameter values that can be floats as floats
                    value = float(value)
                except:  # otherwise leave as strings
                    pass                
                             
                table.set_attr(parameter, value)  # set hdr parameters as attributes of the .dat table
                                  
    with open(dat_file, 'r') as f:
        spec = np.fromfile(f, np.float32)        
        data_point = table.row
        wavenum = table.attrs.wstart
        
        for line in spec:
            data_point['wavenumber'] = wavenum
            data_point['snr'] = line
            wavenum += table.attrs.delw
            data_point.append()
            
            



# def create_lin_table():
#     with open('test.cln', 'r') as lin_file:
#         lin_lines = lin_file.readlines()
    
#     for line in lin_lines[4:]:  # skip header
  
  
        
create_spectrum_table(fileh, spectra_group, dat_file, hdr_file)
fileh.close()