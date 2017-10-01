from multiprocessing import Pool
from multiprocessing import Process,Manager
import os, time, random
import icComVar as icVar
import pyparsing as pp
import re
import fileinput as fi
import matplotlib.pyplot as plt
import numpy as np
import json
import multiprocessing as mp

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

#def comp2dictRe(comp,compHash):
#    compList = comp.split("+")
#    print compList
    #compHash[instName]= {}
    #instName = compList[1].split()[1]
    #compHash[instName]["REFNAME"] =
    #compHash[instName]["STATUS"] = status
    #compHash[instName]["LOCATION"] = location
    #compHash[instName]["ORITATION"] = oritation
    #if len(result[0][0]) > 3:
    #    for i in range(3,len(result[0][0]),2 ):
    #        #print "key value i ",i, result[0][0][i], result[0][0][i+1]
    #        key = result[0][0][i]
    #        value = result[0][0][i+1]
    #        compHash[instName][key] = value
def comp2dict(comp,compHash):
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
def net2dict(net,netHash):
    itemList = net.split("+")
    netPin = re.split("[\)\(]",itemList[0])
    for p in netPin:
        pinList = p.split()
        if p.find("- ") == 0:
            netName = pinList[1]
            netHash[netName] = {}
            netHash[netName]["PIN"] = []
        elif len(pinList) == 2:
            netHash[netName]["PIN"].append(pinList)
        #else:
        #   print pinList
    for i in range(1,len(itemList)):
        attrList = itemList[i].split()
        if attrList[0].find("USE") > -1 :
            netHash[netName]["USE"] = attrList[1]
        elif attrList[0].find("NONDEFAULTRULE") > -1:
            netHash[netName]["NONDEFAULTRULE"] = attrList[1]
        elif  re.search("[ROUTED|FIXED]",attrList[0]) > -1:
            skip = 0
        else:
            print "New attr", itemList[i]










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
            if result[0][0][i] is "LAYER":
                bkgHash["ROUTE"][bkgName]["LAYER"] = result[0][0][i+1]
            elif re.search("SPACING",result[0][0][i]):
                bkgHash["ROUTE"][bkgName]["SPACING"] = result[0][0][i+1]
            elif re.search("POLYGON",result[0][0][i]):
                bkgHash["ROUTE"][bkgName]["SHAPE"] = result[0][0][i+1]


def via2dict(via,viaHash):
    #print "paring via:", via
    result = pattern_match(icVar.viaDefine, via)
    #print "paring result", result
    viaName = result[0][0][0]
    for i in range(1,len( result[0][0])):
        layer = result[0][0][i][1]
        polygon = result[0][0][i][2]
        viaHash[viaName] = {}
        viaHash[viaName]["RECT"] = {}
        viaHash[viaName]["RECT"][i]= {}
        viaHash[viaName]["RECT"][i]["LAYER"] = layer
        viaHash[viaName]["RECT"][i]["SHAPE"] = polygon


if __name__=='__main__':
    #defFileName = 'C:/parser_case/COMPS.def.gz'
    defFileName = 'C:/parser_case/Place.def.gz'
    defFile = fi.FileInput(defFileName, openhook=fi.hook_compressed)
    pool = Pool(4)
    allItem = []
    singleItem = []
    skipComp = 1
    skipPin = 1
    skipVia = 1
    skipNets = 0
    skipBkg = 1
    for line0 in defFile:
        if defFile.filelineno() % 100000 == 0 : print "Reading Def", defFile.filelineno()
        if line0.find('PINS') == 0 and skipPin == 0 :
            for line1 in defFile:
                if line1.find('END PINS') == 0:
                    print "Parsing PINS"
                    pinHash = {}
                    for pin in allItem:
                        pin2dict(pin,pinHash)
                        print "\tparsing pin", pin
                    allItem = []
                    singleItem = []
                    with open('pin.json', 'w') as fp:
                       json.dump(pinHash,fp,indent=1)
                    fp.close()
                    print "Finished Parsing PINS", len(allItem)
                    break
                else:
                    if line1.find(';') > -1:
                        singleItem.append(line1.strip())
                        singlePinString = ''.join(singleItem)
                        allItem.append(singlePinString)
                        singleItem = []
                    else:
                        singleItem.append(line1.strip())
        elif line0.find("COMPONENTS") == 0 and skipComp == 0 :
            for line1 in defFile:
                if defFile.filelineno() % 100000 == 0: print "Reading Comp",defFile.filelineno()
                if line1.find('END COMPONENTS') == 0:
                    print "Start To Match COMPONENT"
                    compHash = {}
                    for i in range(len(allItem)):
                        if i % 100000 == 0 : print "parsed ",i
                        comp = allItem[i].split("+")
                        for i in range(len(comp)):
                            compItem = comp[i]
                            if compItem.find("- ") > -1:
                                #print type(compItem), compItem.split()
                                compList = compItem.split()
                                instName = compList[1]
                                refName = compList[2]
                                compHash[instName] = {}
                                compHash[instName]["REFNAME"] = refName
                                #print icVar.placeStatus, type(icVar.placeStatus)
                            elif icVar.rePlaceStatus.search(compItem) :
                                #print icVar.rePlaceStatus.search(compItem), compItem.find("PLACED"), compItem
                                compList = compItem.split()
                                #print compItem
                                compHash[instName]["STATUS"] = compList[0]
                                compHash[instName]["LOCATION"] = compList[2:4]
                                compHash[instName]["ORITATION"] = compList[5]
                    allItem = []
                    singleItem = []

                    with open('comp.json','w') as fp:
                       json.dump(compHash,fp,indent=1)
                    fp.close()
                    print "Finished Parsing COMPONMENT"
                    break
                else:
                    if line1.find(';') > -1:
                        singleItem.append(line1.strip())
                        singleCompString = ''.join(singleItem)
                        allItem.append(singleCompString)
                        singleItem = []
                    else:
                        singleItem.append(line1.strip())
        elif  line0.find("BLOCKAGES") == 0 and skipBkg == 0 :
            for line1 in defFile:
                if line1.find('END BLOCKAGES') == 0:
                    print "Start To Match Blockage"
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
                    print "Finished Parsing Blockage"
                    break
                else:
                    if line1.find(";") > -1:
                        singleItem.append(line1.strip())
                        singleCompString = ''.join(singleItem)
                        allItem.append(singleCompString)
                        singleItem = []
                    else:
                        singleItem.append(line1.strip()+" + ")
        elif line0.find("VIAS") == 0  and skipVia == 0:
            for line1 in defFile:
                if line1.find("END VIAS") == 0:
                    print "Start To Match VIAS"
                    viaHash = {}
                    for via in allItem:
                        via2dict(via,viaHash)
                    allItem = []
                    singleItem = []
                    with open('via.json','w') as fp:
                        json.dump(viaHash,fp,indent=1)
                    fp.close()
                    print "Finished Parsing Blockage"
                    break
                else:
                    if line1.find(";") > -1:
                        singleItem.append(line1.strip())
                        singleCompString = ''.join(singleItem)
                        allItem.append(singleCompString)
                        singleItem = []
                    else:
                        singleItem.append(line1.strip()+" ")

    #with open('pin.json', 'r') as fp:
    #   output = json.load(fp)
        elif line0.find("NETS ") == 0 and skipNets == 0:
            for line1 in defFile:
                if line1.find('END NETS') == 0:
                    print "Parsing Nets"
                    netHash = {}
                    for i  in range(len(allItem)):
                        net2dict(allItem[i],netHash)
                    singleItem = []
                    allItem = []
                    with open('net.json', 'w') as fp:
                        json.dump(netHash, fp, indent=1)
                    fp.close()
                    break
                else:
                    if line1.find(";") > -1:
                        singleItem.append(line1.strip())
                        singleString = "".join(singleItem)
                        allItem.append(singleString)
                        singleItem = []
                    else:
                        singleItem.append(line1.strip())






