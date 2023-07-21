""" These classes are the descriptors for the hdf5 file tables to be generated from user selected starting files"""

import tables as tb
import numpy as np
import pandas as pd
import h5py
from struct import unpack
import os


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
    
    
    
class LineSpec(tb.IsDescription):
    wavenumber = tb.Float64Col()
    snr = tb.Float32Col()
    width = tb.Float32Col()
    damping = tb.Float32Col()
    eq_width = tb.Float32Col()
    itn = tb.Int16Col()
    ihold = tb.Int16Col()
    tags = tb.StringCol(4)
    epstot = tb.Float32Col()
    epsevn = tb.Float32Col()
    epsodd = tb.Float32Col()
    epsran = tb.Float32Col()
    spare = tb.Float32Col()
    ident = tb.StringCol(32)
    
class MergedLinesTable(tb.IsDescription):
    """Descriptor for the merged linelist file made from the combined observed and calculated lines."""
    log_gf = tb.Float64Col()
    wavenumber = tb.Float64Col()
    lower_desig = tb.StringCol(32)
    upper_desig = tb.StringCol(32)
    intensity = tb.StringCol(32)
    upper_energy = tb.Float64Col()
    lower_energy = tb.Float64Col()
    ritz_wavenumber = tb.Float64Col()
    

fileh = tb.open_file('test.h5', 'w')
# fileh = tb.open_file('test.h5', 'r')

## Creating main groups in hdf5 file
levels_group = fileh.create_group(fileh.root, 'levels', 'Levels')
spectra_group = fileh.create_group(fileh.root, 'spectra', 'Spectra')
previous_lines_group = fileh.create_group(fileh.root, 'previousLines', 'Previous Lines')
calculations_group = fileh.create_group(fileh.root, 'calculations', 'Calculations')
matched_lines_group = fileh.create_group(fileh.root, 'matched_lines', 'Matched Lines')

spectrum_files = [os.path.join('CrII_data', 'Cr042416.005_r'),
                  os.path.join('CrII_data', 'Cr061011.007_c'),
                  os.path.join('CrII_data', 'Cr102700.001_r'),
                  os.path.join('CrII_data', 'Cr102700.003_r'),
                  os.path.join('CrII_data', 'Cr110600.001_r'),
                  os.path.join('CrII_data', 'cr110600.003_r'),
                  os.path.join('CrII_data', 'Cr110700.001_r'),
                  os.path.join('CrII_data', 'Cr110700.002_r'),
                  os.path.join('CrII_data', 'Cr120800.001_r')]

lev_file = 'test_lev.csv'
calc_file = 'test_calc.csv'
prev_file = 'test_prev.csv'

def create_spectrum_table(hdf5file, files):
    for file in files:
        filename = file.split('\\')[-1]
        dat_file = file + '.dat'
        hdr_file = file + '.hdr'
        
        spectrum_group = hdf5file.create_group(spectra_group, filename, filename)  # create the group for the spectra
        table = hdf5file.create_table(spectrum_group, 'spectrum', SpectrumTable, filename)  # create table for .dat file

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


def create_lin_bin_table(hdf5file, files, group=None):
    
    ### TODO: Need to make this automatically select between the correct file type and do the correct conversion. i.e. merge with create_lin_table. ###
    
    for file in files:
        filename = file.split('\\')[-1]
        flin = open(file + ".lin", "rb")
        #tags=[4]                   # Create the array for the 'tags' parameters.

        nlin=unpack("i",flin.read(4))[0]          # No. of lines in the file
        linlen = unpack("i",flin.read(4))[0]      # Total number of valid data in file

        # Next line is to make up total of 320 bytes that is the prefix in the file
        tmp = flin.read(312)

        #
        # Now read in all the lines and add to the pytable
        #
        spectrum_group = hdf5file.get_node(spectra_group, filename) 
        table = hdf5file.create_table(spectrum_group, 'linelist', LineSpec, filename)  # create table for .dat file   
        
        row = table.row
        for i in range(nlin) :
            row['wavenumber'], row['snr'], row['width'], row['damping'], row['itn'], row['ihold'] = unpack("dfffhh", flin.read(24))
            row['tags'] = flin.read(4)
            row['epstot'], row['epsevn'], row['epsodd'], row['epsran'], row['spare'] = unpack("fffff", flin.read(20))
            row['ident'] = flin.read(32)
            row.append()
        table.flush()          
        flin.close()


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
    
def create_matched_lines_table(hdf5file):
    """Matches calculated lines with previously observed lines. Creates a new table with the matched lines"""
    calculated_lines = pd.DataFrame(hdf5file.root.calculations.lines.read())  # read into a numpy structured array and convert to Dataframe
    previous_lines = pd.DataFrame(hdf5file.root.previousLines.lines.read())
    levels = pd.DataFrame(hdf5file.root.levels.levels.read())

    # Merge lists together - matching the calc log_gf to observed lines. ""Outer" ensures all lines are kept.
    matched_lines = pd.merge(calculated_lines, previous_lines[['intensity', 'lower_desig', 'upper_desig', 'wavenumber']], how="outer", on=['upper_desig', 'lower_desig'])
    matched_lines = pd.merge(matched_lines, levels[['desig', 'energy']].rename(columns={'desig':'upper_desig', 'energy': 'upper_energy'}), on='upper_desig', how='left')
    matched_lines = pd.merge(matched_lines, levels[['desig', 'energy']].rename(columns={'desig':'lower_desig', 'energy': 'lower_energy'}), on='lower_desig', how='left')
    matched_lines['ritz_wavenumber'] = matched_lines['upper_energy'] - matched_lines['lower_energy']
        
    table = hdf5file.create_table(matched_lines_group, 'lines', MergedLinesTable, 'Matched Lines')
  
    row = table.row
    for i, line in matched_lines.iterrows():  # method needed to iterrate over a DataFrame
        row['log_gf']= line['log_gf']
        row['wavenumber'] = line['wavenumber']
        row['lower_desig'] = line['lower_desig']
        row['upper_desig'] = line['upper_desig']
        row['intensity'] = line['intensity']
        row['upper_energy'] = line['upper_energy']
        row['lower_energy'] = line['lower_energy']
        row['ritz_wavenumber'] = line['ritz_wavenumber']
        row.append()
    table.flush() 

                 
create_spectrum_table(fileh, spectrum_files)
create_lin_bin_table(fileh, spectrum_files)
create_lev_table(fileh, lev_file)
create_calc_table(fileh, calc_file)
create_prev_idents_table(fileh, prev_file)
create_matched_lines_table(fileh)

fileh.close()