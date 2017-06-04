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
    result = pattern.searchString(target_string).asList()
    return result

if __name__=='__main__':
    defFile = 'C:/parser_case/Place.def'
    defFP = fi.FileInput(defFile, openhook=fi.hook_compressed)
    p = Pool(4)
    for line0 in defFP:
        if line0.startswith('PINS'):
            allPin = []
            singlePin = []
            print "Reading PINS"
            for line1 in defFP:
                if line1.startswith('END PINS'):
                    print "Analyzing pins", len(allPin)
                    results = [p.apply_async(pattern_match, args=(icVar.pinDefine, pin)) for pin in allPin]
                    output = [pt.get() for pt in results]
                    # print output
                    p.close()
                    p.join()
                    print len(output), type(output), output[0]
                    # with open('pin.json', 'w') as fp:
                    #   json.dump(output, fp)
                    # fp.close()
                    break
                elif line1.startswith(" -"):
                    singlePin.append(line1)
                    if line1.endswith(';'):
                        singlePinString = ''.join(singlePin)
                        allPin.append(singlePinString)
                        singlePin = []
                elif line1.endswith(';'):
                    singlePin.append(line1)
                    singlePinString = ''.join(singlePin)
                    allPin.append(singlePinString)
                    singlePin = []
                elif len(singlePin) > 0:
                    singlePin.append(line1)
                else:
                    print "Read Pin Error:", line1
            print allPin

    #with open('pin.json', 'r') as fp:
    #   output = json.load(fp)



