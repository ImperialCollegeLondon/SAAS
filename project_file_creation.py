""" These classes are the descriptors for the hdf5 file tables to be generated from user selected starting files"""

import tables as tb
import numpy as np

class EnergyTable(tb.IsDescription):
    """Descriptor for energy level data table"""
    desig = tb.StringCol(32)
    j = tb.Float64Col()
    energy = tb.Float64Col()
    energy_unc = tb.Float64Col()
    parity = tb.UInt8Col()
    species = tb.StringCol(8)
    lifetime = tb.Float64Col()
    lifetime_unc = tb.Float64Col()
    
    
class CalculationTable(tb.IsDescription):
    """Descriptor for calcluated lines table"""
    lower_desig = tb.StringCol(32)
    upper_desig = tb.StringCol(32)
    log_gf = tb.Float64Col()
    
    
class PreviousLinesTable(tb.IsDescription):
    """Descriptor for the previously observed line table"""
    wavenumber = tb.Float64Col()
    lower_energy = tb.Float64Col()
    upper_energy = tb.Float64Col()
    lower_desig = tb.StringCol(32)
    upper_desig = tb.StringCol(32)
    #snr = tb.Float64Col()
    intensity = tb.StringCol(32)
    #note = tb.StringCol(64)
    
    
class SpectrumTable(tb.IsDescription):
    """Descriptor for Spectrum .dat table. The .hdr data will all be stored at attributes (attrs) of this table"""
    wavenumber = tb.Float64Col()
    snr = tb.Float64Col()
    
    
class LinelistTable(tb.IsDescription):
    """Descriptor for the linelist file associated with a spectrum. Wavenumber, air and intensity correction will be stored as attributes of this table"""
    line_num = tb.UInt16Col()
    wavenumber = tb.Float64Col()
    snr = tb.Float64Col()
    width = tb.Float64Col()  # in mK (10^-3 cm-1)
    damping = tb.Float64Col()
    eq_width = tb.Float64Col()
    tags = tb.StringCol(8)
    

fileh = tb.open_file('test.h5', 'w')

# Creating main groups in hdf5 file
levels_group = fileh.create_group(fileh.root, 'levels', 'Levels')
spectra_group = fileh.create_group(fileh.root, 'spectra', 'Spectra')
previous_lines_group = fileh.create_group(fileh.root, 'previousLines', 'Previous Lines')
calculations_group = fileh.create_group(fileh.root, 'calculations', 'Calculations')

hdr_file = 'test.hdr'
dat_file = 'test.dat'
lin_file = 'test.cln'
lev_file = 'test_lev.csv'
calc_file = 'test_calc.csv'
prev_file = 'test_prev.csv'

def create_spectrum_table(hdf5file, dat_file, hdr_file):
    spectrum_group = hdf5file.create_group(spectra_group, dat_file[:-4], dat_file[:-4])  # create the group for the spectra
    table = hdf5file.create_table(spectrum_group, 'spectrum', SpectrumTable, dat_file)  # create table for .dat file

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
    
    # Populate .dat table with data points                              
    with open(dat_file, 'r') as f:
        spec = np.fromfile(f, np.float32)        
        wavenum = table.attrs.wstart  # starting wavenumber
       
        data_point = table.row  # gives pointer for starting row in table
        for line in spec:
            data_point['wavenumber'] = wavenum
            data_point['snr'] = line
            wavenum += table.attrs.delw  # increment wavenumber by dispersion
            data_point.append()  # write from I/O buffer to hdf5 file
        table.flush()

def create_lin_table(hdf5file, file, group=None):

    with open(lin_file, 'r') as f:
        header = f.readlines(150)
        if 'NO' in header[0]:
            wavenumber_calib = False
        else:  # !need to change this to provide the correct wavenumber correction factor
            wavenumber_calib = True
        if 'NO' in header[1]:
            air_calib = False
        else:
            air_calib = True
        if 'NO' in header[2]:
            intensity_calib = False
        else:
            intensity_calib = True  
    
    lines = np.genfromtxt(file, dtype=None, skip_header=3, names=True, autostrip=True, usecols=(0,1,2,3,4,5,8), encoding='utf-8')  # all data with columns headers !may want to specify column datatypes 
    spectrum_group = hdf5file.get_node(spectra_group, file[:-4]) 
    table = hdf5file.create_table(spectrum_group, 'linelist', LinelistTable, file)  # create table for .dat file    
    
    table.attrs.wavenumber_correction = wavenumber_calib
    table.attrs.air_correction = air_calib
    table.attrs.intensity_calibration = intensity_calib
    
    row = table.row
    for line in lines:
        row['line_num'] = line['line']
        row['wavenumber'] = line['wavenumber']
        row['snr'] = line['peak']
        row['width'] = line['width']
        row['damping'] = line['dmp']
        row['eq_width'] = line['eq']
        row['tags'] = line['H']  # not the tags column due to the way numpy names columns, but does give the correct value
        row.append()    
    table.flush()
    
def create_lev_table(hdf5file, file):      
    levels = np.genfromtxt(file, delimiter=',', dtype=None, names=True, autostrip=True, encoding='utf-8', skip_header=3)  # all data with columns headers !may want to specify column datatypes 
    table = hdf5file.create_table(levels_group, 'levels', EnergyTable, file)  # create table for .dat file    
    
    with open(file, 'r') as f:   #get and set header attributes
        header = f.readlines()[:3]
        table.attrs.source = header[0].split('=')[-1].strip()
        table.attrs.date = header[1].split('=')[-1].strip()
        table.attrs.info = header[2].split('=')[-1].strip()           
    
    row = table.row
    for level in levels:
        row['desig'] = level['Designation']
        row['j'] = level['J']
        row['energy'] = level['Energy']
        row['energy_unc'] = level['Energy_Unc']
        row['parity'] = level['Parity']
        row['species'] = level['Species']
        row['lifetime'] = level['Lifetime']             
        row['lifetime_unc'] = level['Lifetime_Unc'] 
        row.append()
    table.flush()  
        
        
def create_calc_table(hdf5file, file):
    lines = np.genfromtxt(file, delimiter=',', dtype=None, names=True, autostrip=True, encoding='utf-8', skip_header=3)  # all data with columns headers !may want to specify column datatypes 
    table = hdf5file.create_table(calculations_group, 'lines', CalculationTable, file)  # create table for .dat file    
    
    with open(file, 'r') as f:   #get and set header attributes
        header = f.readlines()[:3]
        table.attrs.source = header[0].split('=')[-1].strip()
        table.attrs.date = header[1].split('=')[-1].strip()
        table.attrs.info = header[2].split('=')[-1].strip()           
    
    row = table.row
    for line in lines:
        row['lower_desig'] = line['lower_desig']
        row['upper_desig'] = line['upper_desig']
        row['log_gf'] = line['log_gf']
        row.append()
    table.flush()  
    
def create_prev_idents_table(hdf5file, file):
    lines = np.genfromtxt(file, delimiter=',', dtype=None, names=True, autostrip=True, encoding='utf-8', skip_header=3)  # all data with columns headers !may want to specify column datatypes 
    table = hdf5file.create_table(previous_lines_group, 'lines', PreviousLinesTable, file)  # create table for .dat file    
    
    with open(file, 'r') as f:   #get and set header attributes
        header = f.readlines()[:3]
        table.attrs.source = header[0].split('=')[-1].strip()
        table.attrs.date = header[1].split('=')[-1].strip()
        table.attrs.info = header[2].split('=')[-1].strip()           
    
    row = table.row
    for line in lines:
        row['wavenumber'] = line['wavenumber']
        row['lower_energy'] = line['lower_energy']
        row['upper_energy'] = line['upper_energy']
        row['lower_desig'] = line['lower_desig']
        row['upper_desig'] = line['upper_desig']
        row['intensity'] = line['intensity']
        row.append()
    table.flush()  
              
create_spectrum_table(fileh, dat_file, hdr_file)
create_lin_table(fileh, lin_file)
create_lev_table(fileh, lev_file)
create_calc_table(fileh, calc_file)
create_prev_idents_table(fileh, prev_file)

fileh.close()