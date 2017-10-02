from multiprocessing import Pool
from multiprocessing import process
import os, time, random
import icComVar as icVar
import pyparsing as pp
import re
import fileinput as fi
import matplotlib.pyplot as plt
import numpy as np
import json

def list_flatten(l, a=None):
    #check a
    if a is None:
        #initialize with empty list
        a = []
    for i in l:
        if isinstance(i, list):
            list_flatten(i, a)
        else:
            a.append(i)
    return a
def get_values(lVals):
    for val in lVals:
        if isinstance(val, list):
            get_values(val)
        else:
            return val

def pattern_match(pattern,target_string):
    #print target_string,pattern
    result = pattern.searchString(target_string).asList()
    return result



if __name__=='__main__':
    lefFileName = 'C:/parser_case/ts07nxpvlogl11hdf057f.lef'
    lefFile = fi.FileInput(lefFileName, openhook=fi.hook_compressed)
    libHash = {}
    libHash["SITE"] = {}
    libHash["MACRO"] = {}

    for line0 in lefFile:
        #print line0
        if line0.find('SITE ') == 0 :
            siteName = line0.split()[1]
            libHash["SITE"][siteName] = {}
            for line1 in lefFile:
                line1 = line1.strip("\n")
                if line1.find('END ') == 0:
                    break
                else:
                    #print "line", line1, type(line1)
                    match = re.match(r'\s*SYMMETRY\s+(\w+)\s+(\w+)',line1)
                    if match:
                        libHash["SITE"][siteName]["SYMMETRY"] = match.group(1), match.group(2)
                    match = re.match(r'\s*CLASS\s+(\w+)', line1)
                    if match:
                        libHash["SITE"][siteName]["CLASS"] = match.group(1)
                    match = re.match(r'\s*SIZE\s+(\S+)\s+BY\s+(\S+)',line1)
                    if match:
                        libHash["SITE"][siteName]["SIZE"] = float(match.group(1)), float(match.group(2))
        elif line0.find('MACRO ') == 0 :
            macroName = line0.split()[1]
            #print macroName
            libHash["MACRO"][macroName] = {}
            # parsing macro cell
            for line1 in lefFile:
                #print "in Macro", line1
                if line1.find("END") > -1:
                    break
                elif line1.find("FIXEDMASK") > -1 :
                        libHash["MACRO"][macroName]["FIXEDMASK"] = 1
                elif line1.find("CLASS ") > -1:
                        libHash["MACRO"][macroName]["CLASS"] =line1.split()[1:-1]
                elif line1.find("FOREIGN") > -1:
                        libHash["MACRO"][macroName]["FOREIGN"] = line1.split()[1:-1]
                elif line1.find("ORIGIN") > -1:
                        libHash["MACRO"][macroName]["ORIGIN"] = line1.split()[1:-1]
                elif line1.find("SYMMETR") > -1:
                        libHash["MACRO"][macroName]["SYMMETRY"] = line1.split()[1:-1]
                elif line1.find("SITE") > -1:
                        libHash["MACRO"][macroName]["SITE"] = line1.split()[1:-1]
                elif line1.find("PIN ") > -1:
                    pinName = line1.split()[1]
                    print "pin ",macroName, pinName
                    libHash["MACRO"][macroName]["PIN"]= {}
                    libHash["MACRO"][macroName]["PIN"][pinName] = {}
                    ##parsing PIN section
                    for line2 in lefFile:
                        #print "in pin",line2
                        if line2.find("END") > -1:
                            break
                        elif line2.find("DIRECTION") > -1:
                            libHash["MACRO"][macroName]["PIN"][pinName]["DIRECTION"] = line2.split()[1]
                        elif line2.find("USE") > -1:
                            libHash["MACRO"][macroName]["PIN"][pinName]["USE"] = line2.split()[1]
                        elif line2.find("SHAPE") > -1:
                            libHash["MACRO"][macroName]["PIN"][pinName]["SHAPE"] = line2.split()[1]
                        elif line2.find("ANTENNAMODEL") > -1:
                            libHash["MACRO"][macroName]["PIN"][pinName]["ANTENNAMODEL"] = line2.split()[1]
                        elif line2.find("ANTENNAGATEAREA") > -1:
                            libHash["MACRO"][macroName]["PIN"][pinName]["ANTENNAGATEAREA"] = line2.split()[1]
                        elif line2.find("PORT") > -1:
                            i = 0
                            libHash["MACRO"][macroName]["PIN"][pinName]["PORT"] = {}
                            # parsing PORT section
                            for line3 in lefFile:
                                #print "in port",line3
                                if line3.find("END") > -1:
                                    break
                                elif line3.find("LAYER") > -1:
                                    layerName = line3.split()[1]
                                    #print layerName
                                    libHash["MACRO"][macroName]["PIN"][pinName]["PORT"][layerName] = {}
                                elif line3.find("RECT") > -1:
                                    #print "rect line", line3 ,i, type(libHash["MACRO"][macroName]["PIN"][pinName]["PORT"][layerName] )
                                    libHash["MACRO"][macroName]["PIN"][pinName]["PORT"][layerName][i] = line3.split()[1:-1]
                                    i = i + 1
                                else:
                                    print "Found incorrect Keyword", line3

                    





    with open('lef.json', 'w') as fp:
        json.dump(libHash, fp, indent=1)
    fp.close()







