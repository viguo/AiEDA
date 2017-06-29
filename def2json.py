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
    #print len(target_string)
    #print pattern
    #print target_string
    result = pattern.searchString(target_string).aslist()
    print result
    return result

if __name__=='__main__':
    defFile = 'C:/parser_case/Place.def'
    defFile = fi.FileInput(defFile, openhook=fi.hook_compressed)
    p = Pool(4)
    for line0 in defFile:
        if line0.find('PINS') == 0:
            allPin = []
            singlePin = []
            for line1 in defFile:
                if line1.find('END PINS') == 0:
                    print "start to match pins", len(allPin)
                    results = [p.apply_async(pattern_match, args=(icVar.pinDefine, pin)) for pin in allPin]
                    #print results
                    #output = [pt.get() for pt in results]
                    #for pt in results:
                    #   print type(pt),pt.get()
                    #print output
                    p.close()
                    p.join()
                    #print len(output), type(output), output[0]
                    #with open('pin.json', 'w') as fp:
                    #   json.dump(output, fp)
                    #fp.close()
                    print "Finished Parsing PINS"
                    break
                else:
                    if line1.find(';') > -1:
                        singlePin.append(line1)
                        singlePinString = ''.join(singlePin)
                        if singlePinString.find("PORT") > 0:
                            print "Multi port", len(singlePinString)
                        else:
                            allPin.append(singlePinString)
                        singlePin = []
                    else:
                        singlePin.append(line1)

'''
                       inFile = open("data.txt")
                        outFile = open("result.txt", "w")
                        buffer = []
                        for line in inFile:
                            if line.startswith("Start"):
                                buffer = ['']
                            elif line.startswith("End"):
                                outFile.write("".join(buffer))
                                buffer = []
                            elif buffer:
                                buffer.append(line)
                        inFile.close()
                        outFile.close()
'''

    #with open('pin.json', 'r') as fp:
    #   output = json.load(fp)



