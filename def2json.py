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

def pin2dict(pin,pinHash):
    pinList = pin.split("+")
    pinName = pinList[0].split()[1]
    pinHash[pinName] = {}
    j = 0
    for i in range(1,len(pinList)):
        pinAttr =  pinList[i].split()
        if len(pinAttr) == 1:
            pinHash[pinName][pinAttr[0]] = 1
        if len(pinAttr) == 2 :
            attrKey = pinAttr[0]
            attrVal = pinAttr[1]
            pinHash[pinName][attrKey] =attrVal
        elif re.match("LAYER", pinAttr[0]) > 0:
            j = j + 1
            termName = 'term_' + str(j)
            result = pattern_match(icVar.portShape,pinList[i])
            #print pinName,termName
            pinHash[pinName][termName] = {}
            pinHash[pinName][termName]["LAYER"] = result[0][0][1]
            pinHash[pinName][termName]["SHAPE"] = result[0][0][2]
        elif re.match("PLACED|FIXED|COVER",pinAttr[0]) > 0:
            result = pattern_match(icVar.portStatus,pinList[i])
            pinHash[pinName][termName]["STATUS"] = result[0][0][0]
            pinHash[pinName][termName]["LOCATION"] = result[0][0][1]
            pinHash[pinName][termName]["ORITATION"] = result[0][0][2]
        #else:
            # "no matched", pinList[i]

def  comp2dict(comp,compHash):
    result = pattern_match(icVar.compDefine,comp)
    #print "result", result
    instName = result[0][0][0]
    refName = result[0][0][1]
    status = result[0][0][2][0]
    location = result[0][0][2][1]
    oritation = result[0][0][2][2]
    compHash[instName]= {}
    compHash[instName]["REFNAME"] = refName
    compHash[instName]["STATUS"] = status
    compHash[instName]["LOCATION"] = location
    compHash[instName]["ORITATION"] = oritation
    if len(result[0][0]) > 3:
        for i in range(3,len(result[0][0]),2 ):
            #print "key value i ",i, result[0][0][i], result[0][0][i+1]
            key = result[0][0][i]
            value = result[0][0][i+1]
            compHash[instName][key] = value

def bkg2dict(bkg,bkgHash):
    bkgList = bkg.split("+")
    if re.search("PLACEMENT", bkg):
        bkgName = "bkg_" + str(len(bkgHash["PLACEMENT"]))
        bkgHash["PLACEMENT"][bkgName] = {}
        result = pattern_match(icVar.bkgType,bkg)
        bkgHash["PLACEMENT"][bkgName]["SHAPE"] = result[0][0][2]
    else:
        bkgName = "rg_" + str(len(bkgHash["ROUTE"]))
        bkgHash["ROUTE"][bkgName] = {}
        result = pattern_match(icVar.layerBkg, bkg)
        for i in range(0,len(result[0][0]),2):
            #print i, result[0][0][i]
            if result[0][0][i] is "LAYER":
                bkgHash["ROUTE"][bkgName]["LAYER"] = result[0][0][i+1]
            elif re.search("SPACING",result[0][0][i]):
                bkgHash["ROUTE"][bkgName]["SPACING"] = result[0][0][i+1]
            elif re.search("POLYGON",result[0][0][i]):
                bkgHash["ROUTE"][bkgName]["SHAPE"] = result[0][0][i+1]
        #bkgHash["ROUTE"][bkgName]["LAYER"] = result[0][0][1]
        #bkgHash["ROUTE"][bkgName]["SPACING"] = result[0][0][3]
        #bkgHash["ROUTE"][bkgName]["SHAPE"] = result[0][0][5]
        #print bkgHash

    #print  bkgHash
    # restructure the bgk


if __name__=='__main__':
    defFile = 'C:/parser_case/Place.def'
    defFile = fi.FileInput(defFile, openhook=fi.hook_compressed)
    p = Pool(4)
    allItem = []
    singleItem = []
    for line0 in defFile:
        if line0.find('PINS') == 0:
            for line1 in defFile:
                if line1.find('END PINS') == 0:
                    print "start to match pins", len(allItem)
                    pinHash = {}
                    for pin in allItem:
                        pin2dict(pin,pinHash)
                    allItem = []
                    singleItem = []
                    with open('pin.json', 'w') as fp:
                       json.dump(pinHash,fp,indent=1)
                    fp.close()
                    print "Finished Parsing PINS"
                    break
                else:
                    if line1.find(';') > -1:
                        singleItem.append(line1.strip())
                        print singleItem
                        singlePinString = ''.join(singleItem)

                        allItem.append(singlePinString)
                        singlePin = []
                    else:
                        singleItem.append(line1.strip())
        elif line0.find("COMPONENTS") == 0:
            for line1 in defFile:
                if line1.find('END COMPONENTS') == 0:
                    print "start to match COMPONENT"
                    compHash = {}
                    for comp in allItem:
                        comp2dict(comp,compHash)
                    allItem = []
                    singleItem = []
                        #p.apply_async(comp2dict, args=(comp, compHash))
                    with open('comp.json','w') as fp:
                       json.dump(compHash,fp,indent=1)
                    fp.close()
                    print "Finished Parsing COMP"
                    break
                else:
                    if line1.find(';') > -1:
                        singleItem.append(line1.strip())
                        singleCompString = ''.join(singleItem)
                        allItem.append(singleCompString)
                        singleItem = []
                    else:
                        singleItem.append(line1.strip())
        elif  line0.find("BLOCKAGES") == 0:
            for line1 in defFile:
                if line1.find('END BLOCKAGES') == 0:
                    print "start to match Blockage"
                    bkgHash = {}
                    bkgHash["ROUTE"] = {}
                    bkgHash["PLACEMENT"] = {}
                    for bkg in allItem:
                        bkg2dict(bkg,bkgHash)
                    allItem = []
                    singleItem = []
                    #print bkgHash
                    with open('bkg.json','w') as fp:
                        json.dump(bkgHash,fp,indent=1)
                    fp.close()
                    print "Finished parsing Blockage"
                    break
                else:
                    if line1.find(";") > -1:
                        singleItem.append(line1.strip())
                        singleCompString = ''.join(singleItem)
                        allItem.append(singleCompString)
                        singleItem = []
                    else:
                        singleItem.append(line1.strip()+" + ")
    #with open('pin.json', 'r') as fp:
    #   output = json.load(fp)



