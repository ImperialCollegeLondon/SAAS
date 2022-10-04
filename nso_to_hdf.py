#!/usr/bin/env python

from tables import *
import h5py
import numpy as np
import sys
from os.path import exists
from struct import unpack
import matplotlib.pyplot as plt

class LineSpec(IsDescription):
    sig = Float64Col()
    xint = Float32Col()
    width = Float32Col()
    dmping = Float32Col()
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

    return(sp)

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
        linelist_group = hdf_file.create_group("/","linelists")
        linel = hdf_file.create_table(linelist_group, "linelist1", LineSpec,"Original linelist")
        sp = linel.row             # Write the linelists to the tables

        read_linelist(specfile,sp)
        linel.flush()

    else:
        print("No linelist found")

    hdf_file.close()
    return()

def plot_spectrum(spec,header):
    fig,ax = plt.subplots()
    wstart = float(header["wstart"])
    wstop = float(header["wstop"])
    delw = float(header["delw"])
    wnum=list(np.arange(wstart,wstop+delw,delw))
    print(len(wnum))
    ax.scatter(wnum,spec)
    ax.set(xlabel="Wavenumber (cm-1)",ylabel="Relative intensity")
    plt.show()




#
# Main program
#

#     if len(sys.argv) != 2:
#         print("Usage: 'python nos6_to_hdf5.py <filename>', with no extension to the filename")
#         sys.exit()
#     else:
#         specfile = sys.argv[1]
#         #
#         # Strip off any extension that describes the file
#         #
#
#     header = {}
#     linel=[]
#
#     #
#     # Open the header and use it to create the metadata
#     #
#     if exists(specfile + ".hdr"):
#         hdr = read_header(specfile + ".hdr")
#     else:
#         print("No header file found, hdf5 file not created")
#         exit()
#     #
#     # Open the spectrum file and read in the spectrum.
#     #
#     if exists(specfile + ".dat"):
#         spec = read_data(specfile + ".dat")
#     else:
#         print("No data file found. ")
#         exit()
#
