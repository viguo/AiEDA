import os, time, random
import sys; sys.path.insert(0, os.getenv('FLOW_DIR','/tool/aticad/1.0/flow/TileBuilder') + '/lib')
from multiprocessing import Pool
from multiprocessing import Process,Manager

import icComVar as icVar
import pyparsing as pp
import re
import fileinput as fi
import matplotlib.pyplot as plt
import numpy as np
import json
import multiprocessing as mp
import glob
from Bom import Bom


def listFlatten(l, a=None):
    #check a
    if a is None:
        #initialize with empty list
        a = []
    for i in l:
        if isinstance(i, list):
            listFlatten(i, a)
        else:
            a.append(i)
    return a
def getValues(lVals):
    for val in lVals:
        if isinstance(val, list):
            getValues(val)
        else:
            return val
def loadJson(filePath):
    # open JSON file and parse contents
    print "Lading json",filePath
    start_time = time.time()
    fh = open(filePath,'r')
    data = json.load(fh)
    fh.close()

    print "\t Loading time :", int(time.time() - start_time), "S"

    return data

def saveJson(Json,fileName):
    with open(fileName, 'w') as fp:
       json.dump(Json, fp, indent=1)

def patternMatch(pattern,target_string):
    #print target_string,pattern
    result = pattern.searchString(target_string).asList()
    return result

def pin2dict(pin):
    pinHash = {}
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
            result = patternMatch(icVar.portShape,pinList[i])
            #print pinName,termName
            pinHash[pinName][termName] = {}
            pinHash[pinName][termName]["LAYER"] = result[0][0][1]
            pinHash[pinName][termName]["SHAPE"] = result[0][0][2]
        elif re.match("UNPLACED",pinAttr[0]) > 0:
            result = patternMatch(icVar.portStatus, pinList[i])
            pinHash[pinName][termName]["STATUS"] = result[0][0][0]

        elif re.match("PLACED|FIXED|COVER",pinAttr[0]) > 0:
            result = patternMatch(icVar.portStatus,pinList[i])
            pinHash[pinName][termName]["STATUS"] = result[0][0][0]
            pinHash[pinName][termName]["LOCATION"] = result[0][0][1]
            pinHash[pinName][termName]["ORITATION"] = result[0][0][2]
    return  pinHash
def comp2dict(comp):
    compHash = {}
    compList = comp.split("+")
    instName,refName = compList[0].split()[1:3]

    if refName.find("_FILL") > -1:
        return compHash
    else:
        compHash[instName] = {}
        compHash[instName]["REFNAME"] = refName
        # print icVar.placeStatus, type(icVar.placeStatus)
        for i in range(1,len(compList)):
            attrList = compList[i].split()
            if attrList[0] == "UNPLACED":
                compHash[instName]["STATUS"] = "UNPLACED"
            elif re.search("PLACED|FIXED|COVER",attrList[0]) :
                # print icVar.rePlaceStatus.search(compItem), compItem.find("PLACED"), compItem
                # print compItem
                compHash[instName]["STATUS"] = attrList[0]
                compHash[instName]["LOCATION"] = attrList[2:4]
                compHash[instName]["ORITATION"] = attrList[5]
            if attrList[0] == "SOURCE":
                compHash[instName]["SOURCE"] = attrList[1]
        return compHash
def net2dict(net):
    netHash = {}
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
        elif  re.search(r"[ROUTED|FIXED|SHAPE|MASK|RECT]",attrList[0]):
            skip = 0
        else:
            print "New attr", attrList[0]
    return netHash
def bkg2dict(bkg):
    bkgHash = {}
    bkgList = bkg.split("+")
    if re.search("PLACEMENT", bkg):
        bkgName = "bkg_" + str(len(bkgHash))
        bkgHash[bkgName] = {}
        result = patternMatch(icVar.bkgType,bkg)
        bkgHash[bkgName]["SHAPE"] = result[0][0][2]
    else:
        bkgName = "rg_" + str(len(bkgHash))
        bkgHash[bkgName] = {}
        result = patternMatch(icVar.layerBkg, bkg)
        for i in range(0,len(result[0][0]),2):
            if result[0][0][i] is "LAYER":
                bkgHash[bkgName]["LAYER"] = result[0][0][i+1]
            elif re.search("SPACING",result[0][0][i]):
                bkgHash[bkgName]["SPACING"] = result[0][0][i+1]
            elif re.search("POLYGON",result[0][0][i]):
                bkgHash[bkgName]["SHAPE"] = result[0][0][i+1]
    return bkgHash
def via2dict(via):
    #print "paring via:", via

    viaHash = {}
    result = patternMatch(icVar.viaDefine, via)
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
    return viaHash

def module2dict(module):
    moduleHash = {}
    mList = module.split(";")
    mitem = mList[0]
    moduleName = mitem.split()[1]
    portList = re.split("[\(\)]", mitem)[1]
    #print "PORT LIST",moduleName, portList.split(",")[0],"END"
    moduleHash[moduleName] = {}
    moduleHash[moduleName]["PORT"] = {}
    moduleHash[moduleName]["NET"] = {}
    moduleHash[moduleName]["INST"] = {}
        # print moduleName
    for portName in portList.split(","):
        portName = portName.strip()
        moduleHash[moduleName]["PORT"][portName] = {}
    for item in mList[1:]:
        rePortWire= re.compile(r"(^input|^output|^inout|^wire)\s+(.*)")
        reInstVlg = re.compile(r"(\w+)\s+(\w+)\s+\((.*)\)\s*")
        portWire = re.match(r"(^input|^output|^inout|^wire)\s+(.*)",item)
        #print "Port DIR: ", port
        if portWire :
            itemP = portWire.group(0)
            dir = itemP.split()[0]
            if dir == "wire":
                attr = "NET"
            else:
                attr = "PORT"
            ### parsing input
            if itemP.find("[") > -1:
                ### is a buse
                #print "Parsing input Bus:", itemP
                busWidth = itemP.split()[1]
                for portName in itemP.split()[2:]:
                    portName = portName.strip()
                    #print "module ,port", moduleName,portName, item
                    if attr == "NET":
                        moduleHash[moduleName]["NET"][portName] = {}
                        moduleHash[moduleName]["NET"][portName]["PINS"] = {}
                    else:
                        moduleHash[moduleName]["PORT"][portName]["DIR"] = dir
                        moduleHash[moduleName]["PORT"][portName]["WIDTH"] = busWidth

                        moduleHash[moduleName]["NET"][portName] = {}
                        moduleHash[moduleName]["NET"][portName]["PINS"] = portName
            else:
                #print "Parsing input Signal", item
                for portName in itemP.split()[1:]:
                    portName = portName.strip()
                    #print "PortName", portName, attr,dir
                    if attr == "NET":
                        moduleHash[moduleName]["NET"][portName] = {}
                        moduleHash[moduleName]["NET"][portName]["PINS"] = []
                    else:
                        moduleHash[moduleName]["PORT"][portName]["DIR"] = dir
                        moduleHash[moduleName]["PORT"][portName]["WIDTH"] = 0
                        moduleHash[moduleName]["NET"][portName] = {}
                        moduleHash[moduleName]["NET"][portName]["PINS"] = []
                        moduleHash[moduleName]["NET"][portName]["PINS"].append(portName)
        else :
            ## instance/module instantial
            #print item
            inst = reInstVlg.match(item)
            if inst:
                refName = inst.group(1)
                instName = inst.group(2)
                moduleHash[moduleName]["INST"][instName] = {}
                moduleHash[moduleName]["INST"][instName]["PIN"] = {}
                moduleHash[moduleName]["INST"][instName]["REFNAME"] = refName
                pins = inst.group(3)
                #print refName,instName
                for pn in pins.split(".")[1:]:
                    pl = re.split("[\(\)]",pn)
                    pin, net = pl[0],pl[1]
                    #print "\t", pin ,net
                    moduleHash[moduleName]["INST"][instName]["PIN"][pin] = net
                    if net == "1\'b0": net = "TIEL"
                    if net == "1\'b1": net = "TIEH"
                    if net.find("\.") > -1:
                        print "pinBus", net
                    else:
                        if net in moduleHash[moduleName]["NET"]:
                            moduleHash[moduleName]["NET"][net]["PINS"].append(instName+"/"+pin)
                        else:
                            moduleHash[moduleName]["NET"][net] = {}
                            moduleHash[moduleName]["NET"][net]["PINS"] = []
                            moduleHash[moduleName]["NET"][net]["PINS"].append(instName+"/"+pin)
    return moduleHash
def instRefName(moduleHash,instName):
    topName = moduleHash["TOP"]
    hierNameList = instName.split("/")

    if hierNameList[0] in moduleHash[topName]["INST"]:
        refName = moduleHash[topName]["INST"][hierNameList[0]]["REFNAME"]
        print "debug: ", hierNameList[0]
        if moduleHash[topName]["INST"][hierNameList[0]]["isLeaf"] == 1:
            return refName
        else:
            for moduleName in hierNameList[1:-1]:
                refName = moduleHash[refName]["INST"][moduleName]["REFNAME"]
            return refName
    else:
        print "Not found inst", instName
        return "ERROR"

def moduleCells(moduleHash):
    print "Getting Flat Cells"
    flatCellsHash = {}
    hierName = []
    def subModuleCells(moduleName,moduleHash):
        subFlatCells = []
        for instName in moduleHash[moduleName]["INST"]:
            refName = moduleHash[moduleName]["INST"][instName]["REFNAME"]
            if refName not in moduleHash:
                subFlatCells.append(instName)
                moduleHash[moduleName]["INST"][instName]["isLeaf"] = 1
            else:
                moduleHash[moduleName]["INST"][instName]["isLeaf"] = 0
                hierCells = subModuleCells(refName,moduleHash)
                newFlatCells = map(lambda x: instName+"/"+x,hierCells)
                subFlatCells.extend(newFlatCells)
        return subFlatCells

    flatCells = []
    for module in moduleHash:
        if module == "TOP": continue
        for instName in moduleHash[module]["INST"]:
            refName = moduleHash[module]["INST"][instName]["REFNAME"]
            if refName not in moduleHash:
                flatCells.append(instName)
            else:
                ## find submodule instance with prefix instName
                hierName.append(instName)
                hierCell = (subModuleCells(refName,moduleHash))
                newHierCell = map(lambda x: instName+"/"+x,hierCell)
                flatCells.extend(newHierCell)

    #saveJson(moduleHash,"./json/module.tmp.json")
    print "len",len(flatCells)
    for i in range(0,len(flatCells)-1):
        inst = flatCells[i]
        flatCellsHash[inst] = {}
        #flatCellsHash[inst]["REFNAME"] = instRefName(moduleHash,inst)

    saveJson(flatCellsHash,"./json/flatCell.json")


def lef2hash(lefFile):
    ##read lef file , return the hash with macro nanme key
    lefHash = {}
    if os.path.isfile(lefFile):
        fp = fi.FileInput(lefFile, openhook=fi.hook_compressed)
        #print "lef2hash ", lefFile
        for line0 in fp:
            # print line0
            if line0.find('MACRO ') == 0:
                macroName = line0.split()[1]
                # print macroName
                lefHash[macroName] = {}
                # parsing macro cell
                for line1 in fp:
                    # print "in Macro", line1
                    if line1.find("END") > -1:
                        break
                    elif line1.find("FOREIGN") > -1:
                        lefHash[macroName]["forigin_x"],lefHash[macroName]["forigin_y"] = line1.split()[2:4]
                    elif line1.find("ORIGIN") > -1:
                        lefHash[macroName]["origin_x"],lefHash[macroName]["origin_y"] = line1.split()[1:3]
                    elif line1.find(" SIZE ") == 0:
                        lefHash[macroName]["width"],lefHash[macroName]["height"]  = float(line1.split()[1:3])
                    elif line1.find("PIN ") > -1:
                        pinName = line1.split()[1]
                        # print "pin ",macroName, pinName
                        lefHash[macroName]["PIN"] = {}
                        lefHash[macroName]["PIN"][pinName] = {}
                        ##parsing PIN section
                        for line2 in fp:
                            # print "in pin",line2
                            if line2.find("END") > -1:
                                break
                            elif line2.find("DIRECTION") > -1:
                                lefHash[macroName]["PIN"][pinName]["DIR"] = line2.split()[1]
                            elif line2.find("USE") > -1:
                                lefHash[macroName]["PIN"][pinName]["USE"] = line2.split()[1]
                            #elif line2.find("SHAPE") > -1:
                            #    lefHash[macroName]["PIN"][pinName]["SHAPE"] = line2.split()[1]
                            #elif line2.find("ANTENNA") > -1:
                            #    antKey, antValue = line2.split()[0], line2.split()[1:-1]
                            #    lefHash[macroName]["PIN"][pinName][antKey] = antValue
                            elif line2.find("PORT") > -1:
                                i = 0
                                # parsing PORT section
                                for line3 in fp:
                                    # print "in port",line3
                                    if line3.find("END") > -1:
                                        break
                                    elif line3.find("LAYER") > -1:
                                        layerName = line3.split()[1]
                                        # print layerName
                                        #lefHash[macroName]["PIN"][pinName]["layer"] = layerName
                                    elif line3.find("RECT") > -1:
                                        # print "rect line", line3 ,i, type(lefHash["MACRO"][macroName]["PIN"][pinName]["PORT"][layerName] )
                                        lefHash[macroName]["PIN"][pinName]["llx"],lefHash[macroName]["PIN"][pinName]["lly"] = line3.split()[-3:-1]
                                        l = line3.split()[2]
                                    #elif line3.find("POLYGON") > -1:
                                    #    lefHash[macroName]["PIN"][pinName]["PORT"][layerName][
                                    #        i] = line3.split()[1:-1]
                                    #    i = i + 1
                                    #else:
                                    #    print "Found incorrect Keyword", line3, lefFile, fp.filelineno()
                            #else:
                                #print "PIN Section Keyword", line2, lefFile, fp.filelineno()
            #elif line0.find('SITE ') == 0:
            #    siteName = line0.split()[1]
            #    libHash["SITE"][siteName] = {}
            #    for line1 in fp:
            #        line1 = line1.strip("\n")
            #        if line1.find('END ') == 0:
            #            break
            #        else:
            #            # print "line", line1, type(line1)
            #            match = re.match(r'\s*SYMMETRY\s+(\w+)\s+(\w+)', line1)
            #            if match:
            #                libHash["SITE"][siteName]["SYMMETRY"] = match.group(1), match.group(2)
            #            match = re.match(r'\s*CLASS\s+(\w+)', line1)
            #            if match:
            #                libHash["SITE"][siteName]["CLASS"] = match.group(1)
            #            match = re.match(r'\s*SIZE\s+(\S+)\s+BY\s+(\S+)', line1)
            #            if match:
            #                libHash["SITE"][siteName]["SIZE"] = float(match.group(1)), float(match.group(2))
    else :
        print "missed file ", lefFile
    return lefHash
def def2hash(defFile):
    dsgHash = {}
    dsgHash["FLOORPLAN"] = {}
    dsgHash["INST"] = {}
    dsgHash["NET"] = {}
    dsgHash["PORT"] = {}
    allItem = []
    singleItem = []

    skipNets = 0
    skipSNets = 1
    skipComp = 0
    skipPin = 0
    skipBkg = 1
    ## skipped as new format not recgnize
    skipVia = 1
    if os.path.isfile(defFile) :
        fp = fi.FileInput(defFile, openhook=fi.hook_compressed)
        print "def2Json :", defFile
        for line0 in fp:
            if line0.find('PINS') == 0 and skipPin == 0 :
                for line1 in fp:
                    if line1.find('END PINS') == 0:
                        if "PORT" not in dsgHash: dsgHash["PORT"] = {}
                        print "\tParsing PINS"
                        for pin in allItem:
                            dsgHash["PORT"].update(pin2dict(pin))
                        allItem = []
                        singleItem = []
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
                for line1 in fp:
                    if line1.find('END COMPONENTS') == 0:
                        print "\tParsing COMPONENT"
                        if "INST" not in dsgHash: dsgHash["INST"] = {}
                        for i in range(len(allItem)):
                            dsgHash["INST"].update(comp2dict(allItem[i]))
                        allItem = []
                        singleItem = []
                        break
                    else:
                        if line1.find(';') > -1:
                            singleItem.append(line1.strip())
                            singleCompString = ''.join(singleItem)
                            allItem.append(singleCompString)
                            singleItem = []
                        else:
                            singleItem.append(line1.strip())
            elif line0.find("BLOCKAGES") == 0 and skipBkg == 0 :
                for line1 in fp:
                    if line1.find('END BLOCKAGES') == 0:
                        print "\tParsing BLOCKAGE"
                        if "BKG" not in dsgHash["FLOORPLAN"]: dsgHash["FLOORPLAN"]["BKG"] = {}
                        for bkg in allItem:
                            dsgHash["FLOORPLAN"]["BKG"].update(bkg2dict(bkg))
                        allItem = []
                        singleItem = []
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
                for line1 in fp:
                    if line1.find("END VIAS") == 0:
                        print "\tParsing VIAS"
                        if "VIA" not in dsgHash["FLOORPLAN"]: dsgHash["FLOORPLAN"]["VIA"] = {}
                        for via in allItem:
                            dsgHash["FLOORPLAN"]["VIA"].update(via2dict(via,))
                        allItem = []
                        singleItem = []
                        break
                    else:
                        if line1.find(";") > -1:
                            singleItem.append(line1.strip())
                            singleCompString = ''.join(singleItem)
                            allItem.append(singleCompString)
                            singleItem = []
                        else:
                            singleItem.append(line1.strip()+" ")
            elif line0.find("NETS ") == 0 and skipNets == 0:
                for line1 in fp:
                    if line1.find('END NETS') == 0:
                        print "\tParsing NETS"
                        for i  in range(len(allItem)):
                            dsgHash["NET"].update(net2dict(allItem[i]))
                        singleItem = []
                        allItem = []
                        break
                    else:
                        if line1.find(";") > -1:
                            singleItem.append(line1.strip())
                            singleString = "".join(singleItem)
                            allItem.append(singleString)
                            singleItem = []
                        else:
                            singleItem.append(line1.strip())
            elif line0.find("SPECIALNETS") == 0 and skipSNets == 0:
                #snet merged in put nets, with special attribute
                for line1 in fp:
                    if line1.find('END SPECIALNETS') == 0:
                        print "\tParsing SPECIALNETS"

                        for i  in range(len(allItem)):
                            dsgHash["NET"] = net2dict(allItem[i])
                        singleItem = []
                        allItem = []
                        break
                    else:
                        if line1.find(";") > -1:
                            singleItem.append(line1.strip())
                            singleString = "".join(singleItem)
                            allItem.append(singleString)
                            singleItem = []
                        else:
                            singleItem.append(line1.strip())

        fp.close()
    return dsgHash

def vlg2hash(vlgFile):
    moduleHash = {}
    if os.path.isfile(vlgFile) and skipNetlist == 0 and os.path.isfile(moduleJsonFile) == 0:
        print "verilog2json", vlgFile
        fp = fi.FileInput(vlgFile, openhook=fi.hook_compressed)
        for line0 in fp:
            if line0.find("module ") == 0:
                moduleCont = ""
                moduleCont += line0.strip()
                for line1 in fp:
                    if line1.find("endmodule") == 0:
                        # print "module", allItem
                        module2dict(moduleCont, moduleHash)
                        break
                    else:
                        moduleCont += line1.strip()
        fp.close()
    else:
        print "Vlg file missed ", os.path.isfile(vlgFile)

    return moduleHash


def i2NetEst2Hash(iccNetEst):
    localHash = {}
    if os.path.isfile(iccNetEst):
        print "iccNetEst2Hash", iccNetEst
        fp = fi.FileInput(iccNetEst, openhook=fi.hook_compressed)
        for line0 in fp:
            if line0.find("the length of net") > -1:
                netName, netLen = line0.split()[4], line0.split()[6]
                localHash[netName]["ESTLEN"] = netLen
        fp.close()
    else:
        print "iccNetEst2Hash missed ", iccNetEst
    return localHash

def i2NetPhy2Hash(i2NetPhy):
    localHash = {}
    if os.path.isfile(iccNetPhy):
        start_time = time.time()
        print "i2NetPhy to Hash", iccNetPhy
        fp = fi.FileInput(iccNetPhy, openhook=fi.hook_compressed)
        for line0 in fp:
            if line0.find("flat_net") > -1:
                netName = line0.split()[1]
                for line1 in fp:
                    if line1.find("route_length") > -1:
                        localHash[netName]["PHYLEN"] = line1.strip()
                        break
        print "\t runtime :", time.time() - start_time, "S"
        fp.close()
    else:
        print "i2NetPhy to Hash missed ", iccNetPhy
    return localHash


def tile2top(tileJsonFile, mpuJsonFile,libJsonFile):
    return 0

def cellDelay(iTran, oLoad,cellName, fromPin, toPin):
    return 0

def lib2hash(libFile):
    libHash = {}
    braceCounter = 0
    if os.path.isfile(libFile):
        fp = fi.FileInput(libFile, openhook=fi.hook_compressed)
        print "lib2hash ", libFile
        for line0 in fp:
            if line0.rstrip().endswith("{") :
                braceCounter += 1
            if line0.rstrip().endswith("}") :
                braceCounter -= 1
            # print line0
            if line0.find('cell (') > -1:
                #print "DEBUG ", fp.filelineno(), line0
                #cellName = line0.split("\"")[1]
                cellName = re.sub(r'[();",]', "", line0).split()[1]
                libHash[cellName] = {}
                #print "cellName ", cellName,fp.filelineno(),braceCounter
                markBrace = braceCounter
                for line1 in fp:
                    line1 = line1.rstrip()
                    if line1.endswith("{"):
                        braceCounter += 1
                    if line1.endswith("}"): braceCounter -= 1
                    if braceCounter < markBrace : break
                    if line1.find("area ") > -1:
                        libHash[cellName]["area"] = line1.split(":")[1]
                    elif line1.find("cell_footprint") > -1:
                        libHash[cellName]["footprint"] = line1.split(":")[1]
                    elif line1.find("dont_use") > -1:
                        libHash[cellName]["dontuse"] = line1.split(":")[1]
                    elif re.search(r"pin\s+\(\w+\)\s+\{",line1) :
                        pinName = re.split("[()]",line1)[1]
                        #print "pinName", pinName, fp.filelineno(),
                        markBrace = braceCounter
                        for line2 in fp:
                            line2 = line2.rstrip()
                            if line2.endswith("{"): braceCounter += 1
                            if line2.endswith("}"): braceCounter -= 1
                            if braceCounter < markBrace: break
                            if line2.find("timing (") > -1:
                                libHash[cellName]["ARC"] = {}
                                markBrace = braceCounter
                                for line3 in fp:
                                    line3 = line3.rstrip()
                                    if line3.endswith("{"): braceCounter += 1
                                    if line3.endswith("}"): braceCounter -= 1
                                    if braceCounter <  markBrace:break
                                    if line3.find("related_pin :") > -1:
                                        relatedPin= re.sub(r'[();",]',"",line3).split()[-1]
                                    elif line3.find("cell_fall ") > -1:
                                        #print relatedPin, pinName, fp.filelineno(), line3
                                        arcName = relatedPin +":" + pinName
                                        libHash[cellName]["ARC"][arcName] = {}
                                        markBrace = braceCounter
                                        for line4 in fp:
                                            line4 = line4.rstrip()
                                            if line4.rstrip().endswith("{"): braceCounter += 1
                                            if line4.rstrip().endswith("}"): braceCounter -= 1
                                            if braceCounter < markBrace: break
                                            if line4.find("index_1 ") > -1:
                                                inputTrans = re.sub(r'[();",]',"",line4.rstrip())
                                                libHash[cellName]["ARC"][arcName]["inputTrans"] = inputTrans.split()[1:]
                                            elif line4.find("index_2 ") > -1:
                                                outputLoad = re.sub(r'[();",]',"",line4.rstrip())
                                                libHash[cellName]["ARC"][arcName]["outputLoad"] = outputLoad.split()[1:]
                                            elif line4.find("values ") > -1:
                                                table = []
                                                while line4.endswith("\\"):
                                                    if line4.find('\"') > -1:
                                                        table.append(line4.split("\"")[1].split())
                                                        table.append(re.sub(r'[()\\",]', "", line4).split())
                                                    line4 = fp.readline().rstrip()

                                                libHash[cellName]["ARC"][arcName]["delayTable"] = table







    else:
        print "miss libFile ",libFile
    return libHash
if __name__=='__main__':
    #rundir = "/proj/ariel_pd_vol88/yaguo/NLD/1016_eco/main/pd/tiles/ECO_1019_run1/"
    tileName = "smu_zcn1_t"
    jsonOut = "/proj/arielc0pd_fct03/yaguo/json/ariel/"
    libBomFile = "/proj/ariel_pd_lib1/TSMC7N/library/lib_PD.D.8/bom.json"
    libBom = Bom(libBomFile)
    libHash = {}
    #libHash["MACRO"] = {}
    #lefJsonFile =  jsonOut + "lefs.json"
    #for item in  libBom.find_designfiles(filetype='lef'):
    #    lefFile = item.get_filename()
    #    ipname = item.get_ipname()
    #    libHash["MACRO"].update(lef2hash(lefFile))
    #lefJsonFile = jsonOut + "lefs.json"
    #saveJson(libHash,lefJsonFile)

    #libJsonFile =  jsonOut + "tt0p65v100c." + "libs.json"
    #libHash["tt0p65v100c"] = {}
    #for item in  libBom.find_designfiles(filetype='lib',libcorner="tt0p65v100c"):
    #    libFile = item.get_filename()
    #    ipname  = item.get_ipname()
    #    corner  = item.get_corner().name()
    #    print "lib ",corner, ipname, libFile
    #
    #    libHash[corner].update(lib2hash(libFile))
    #
    #saveJson(libHash, libJsonFile)

    #newTile.json = tile2top (tile.json, mpu.json)
    #delay = cellDelay (inputTran, ouptuLoad, refName,  fromPin ,toPin)

    fctBomFile = "/proj/ariel_pd_fct3/fct_eco_runs/func_flat_normal/fct087_ECO_Func_Flat_EcoRoute_Nov08/data/bom.json"
    fctBomHash = Bom(fctBomFile)

    libHash["TILE"] = {}
    tileLefFile = jsonOut + "tiles.Lef.json"
    for item in fctBomHash.find_designfiles(filetype='lef'):
        tileName = item.get_ipname()
        lefFile  = item.get_filename()
        #print lefFile, tileName
        libHash["TILE"].update(lef2hash(lefFile))

    saveJson(libHash,tileLefFile)

    for item in fctBomHash.find_designfiles(filetype='def',stage_name='EcoRoute' ,ipname="mpu"):
        tileName = item.get_ipname()
        defFile  = item.get_filename()
        dsgJsonFile    = jsonOut+tileName+".design.json"
        print "loading ", defFile
        dsgHash = def2hash(defFile)
        saveJson(dsgHash,dsgJsonFile)

    for item in fctBomHash.find_designfiles(filetype='def',stage_name='EcoRoute' ,ipname="dfx_dft_t"):
        tileName = item.get_ipname()
        defFile  = item.get_filename()
        dsgJsonFile    = jsonOut+tileName+".design.json"
        print "loading ", defFile
        dsgHash = def2hash(defFile)
        saveJson(dsgHash,dsgJsonFile)

    topHash = loadJson(jsonOut+tileName+".design.json")
    for tile in fctBomHash["ips"]["mpu"]["children"]:
        print "tileName", tile
        loadJson()


'''

            libHash["SITE"] = {}
            lefHash = {}
            lefHash["MACRO"] = {}

            dsgHash = {}

    if os.path.isfile(moduleJsonFile):
        moduleHash = loadJson(moduleJsonFile)
    saveJson(dsgHash, dsgJsonFile)
    dsgHash["MODULE"] = moduleHash
    libJsonFile = "./json/lib.json"
    if os.path.isfile(libJsonFile):
        libHash = loadJson(libJsonFile)

    for lefFile in glob.glob(rundir + "*.lef"):
        lef2hash(lefFile,lefHash)
    saveJson(lefHash,libJsonFile)

    moduleCells(moduleHash)

'''






