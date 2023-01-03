#!/usr/bin/env python

from tables import *
import h5py
import numpy as np
import sys
from os.path import exists
from os.path import *
from struct import unpack
import matplotlib.pyplot as plt

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

#
# This class currently not used - added for future.
#

class Spectrum():
    line = LineSpec()
    spec = float()
    hdr =  []
    response = float()
    phase = float()
    badpt = float()

class EnergyLevel(IsDescription):
    """
    This applies to the current file Cr_BF2.h5, where the level parameters are stored in order
    but with no particular key. It would probably be better to store it with keys.
    """
    desig = StringCol(10)
    J = StringCol(3)
    energy  = StringCol(11)
    uncertainty = StringCol(6)
    parity = StringCol(1)
    lifetime = StringCol(4)
    key = StringCol(10)
    species = StringCol(10)

def read_linelist(specfile,sp):
    #
    #  Read in a linelist and return as a pytable
    #

    flin = open(specfile+".lin","rb")
    tags=[4]                   # Create the array for the 'tags' parameters.

    #
    # Read the header information in the .lin file
    #

    nlin=unpack("i",flin.read(4))[0]          # No. of lines in the file
    print(nlin, "lines in file")
    linlen = unpack("i",flin.read(4))[0]      # Total number of valid data in file

    # Next line is to make up total of 320 bytes that is the prefix in the file
    tmp = flin.read(312)

    #
    # Now read in all the lines and add to the pytable
    #
    for i in range(nlin) :
        sp['sig'],sp['xint'],sp['width'],sp['dmping'],sp['itn'],sp['ihold'] = unpack("dfffhh",flin.read(24))
        sp['tags'] = flin.read(4)
        sp['epstot'],sp['epsevn'],sp['epsodd'],sp['epsran'],sp['spare']=unpack("fffff",flin.read(20))
        sp['ident']=flin.read(32)
        sp.append()

    print(i+1,"lines converted")
    flin.close()

    return(sp)

def read_levels(levfile,lst):
    fintc = open(levfile,"r")
    i=0

    for line in fintc:
        line=line.split()    
        print(line[2],line[3])
        lst['desig'],lst['J'],lst['energy'],lst['uncertainty']=(line[0],line[1],line[2],line[3])
        lst['parity'],lst['lifetime'],lst['key'] = (line[4],line[5],line[6])
        lst['species'] = "Cr II"
        print(lst['energy'],lst['uncertainty'])
        lst.append()
        i=i+1

    return()

def read_intcorr(linfile,lst):
    fintc = open(linfile,"r")
    i=0

    for line in fintc:
        line=line.split()
        if line[0].isdigit():     #Means this is a line and not header information
            lst['sig'],lst['xint'],lst['width'],lst['dmping']=(line[1],line[2],line[3],line[4])
            lst['ew'],lst['itn'],lst['ihold'],lst['tags'] = (line[5],line[6],line[7],line[8])
            lst.append()
            i=i+1

#
# Need some error checking here as well.
# Including parsing the header Lines
#

    print(i,"lines read in")
    fintc.close()
    return(lst)

def read_header(hdrfile):
    #
    # Create the metadata from the header file.
    #
    header = {}
    hdr = open(hdrfile)

    for line in hdr:
        if line[0] == "/" or line[0:3] == "END":
            continue
        if line[0:8] == "continue" :
            val = val + line[9:32]
        else:
            key = line[0:8].rstrip()
            val = line[9:32]
        if line[0:2] == "id":
            val = line[9:80]
        header[key]=val
        header[key+"_comment"] = line[34:80]

    return(header)

def read_data(specfile):
    with open(specfile,"rb") as f:
         spec = np.fromfile(f,np.float32)
#         if len(spec) - int(header["npo"]) != 0 :
#             print(f'No. of points does not match npo: npo = {header["npo"]}, length = {len(spec)}')
#         else:
#             print (f'{len(spec)} points read')

    return(spec)

def read_response(specfile):
    return()

def write_hdf5(specfile,spec,header):
    #
    # Create the hdf5 file, create spectrum group and write the data to a dataset in the spectrum group
    #

#    h5.get_config().track_order=True
    hdf_file = open_file(specfile + '.hdf5','w', title="FT Spectrum")
    spectrum_group = hdf_file.create_group("/","spectrum")
    dataset = hdf_file.create_array(spectrum_group,"spectrum",spec,"original spectrum")

    #
    # Write the metadata to the dataset in the spectrum group
    #

    for key,value in header.items():
        dataset.attrs[key] = value
    #
    # Write the linelist to the hdf5 file if there is one
    #
    if exists(specfile + '.lin'):
        # Add an if block to cope with what to do if group exists.
        linelist_group = hdf_file.create_group("/","linelists")
        linel = hdf_file.create_table(linelist_group, "linelist1", LineSpec,"Original linelist")
        sp = linel.row             # Write the linelists to the tables

        read_linelist(specfile,sp)
        linel.flush()

    else:
        print("No linelist found")

    hdf_file.close()
    return(hdf_file)

def add_intcorr(specfile,linfile):
    tab_name= split(linfile)[1]

    #
    # Is there a better way of doing this than closing the hdf5 file in write_hdf5
    # and re-opening it here?
    # Is there a more flexible way of selecting the hdf5 file, rather than
    # just assuming it's the same as the one written?
    #

    hdf_file = open_file(specfile + '.hdf5','r+', title="FT Spectrum")
    # Needs an if block to make it more robust - what if group exists?
    intcorr_group = hdf_file.create_group("/","intensity calibrated linelists")
    intcorr_table = hdf_file.create_table(intcorr_group, tab_name, LineSpec,linfile)
    lst=intcorr_table.row
    read_intcorr(linfile,lst)
    intcorr_table.flush()

    return()

def add_levels(Lev_hdf5,levfile):
    tab_name = levfile[0]
    hdf_file = open_file(Lev_hdf5,'w',title="Levels")
    lev_group = hdf_file.create_group("/","Levels")
    lev_table = hdf_file.create_table(lev_group,"Cr II levels", EnergyLevel, tab_name)
    lst =lev_table.row
    read_levels(tab_name,lst)
    lev_table.flush()

    return()

def plot_spectrum(spec,header):
    # How do I get it to plot the spectrum in the correct window?
    fig,ax = plt.subplots()
    wstart = float(header["wstart"])
    wstop = float(header["wstop"])
    delw = float(header["delw"])
    wnum=list(np.arange(wstart,wstop,delw))
    print(len(wnum))
    ax.plot(wnum,spec)
    ax.set(xlabel="Wavenumber (cm-1)",ylabel="Relative intensity")
    plt.show()
