#!/usr/bin/env python
""" 
Program to assist in matching levels from two source. 
The routine matches based on energy and J, with a tolerance of 0.2 cm-1.
The output will need to be checked carefully to ensure the levels in the
two files have been correctly matched.

G. Nave, 6th January, 2023.
"""
def match_lev(file1, file2):
    
    levlst=[]

    f  = open(file1,"r")
    for line in f:
        line=line.split()
        levlst.append(line)

    fru = open(file2)

    n = 0
    for line in fru:
        line=line.split()
        mtch = 0
        for i in levlst:
            en = float(line[0].strip("*"))

            if -0.2 < float(i[2]) - en < 0.2 and float(i[1]) == float(line[2]):
                print (line[0],line[1],line[2], en-float(i[2]), i[0])
                n = n+1
                mtch = 1

        if mtch == 0:
            print (line, "not matched")

    print(n, "levels matched")

    return()

# match_lev("cr_ii.lev", "CrII_evens.RU")
