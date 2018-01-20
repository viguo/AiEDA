import os, time, random


#import sys; sys.path.insert(0, os.getenv('FLOW_dir','/tool/aticad/1.0/flow/TileBuilder') + '/lib')
import sys; sys.path.insert(0, os.getenv('FLOW_dir','/home/yaguo/scripts/amdPython3'))
from multiprocessing import Pool
from multiprocessing import Process,Manager
import copy
import icComVar as icVar
import pyparsing as pp
import re
import fileinput as fi
import matplotlib.pyplot as plt
import numpy as np
import json,gzip
import multiprocessing as mp
import glob
from Bom  import Bom, IP
import socket
def params2Json(tileParams):
    paramHash = {}
    with open(tileParams,"rt") as fin:
        for line in fin:
            if line.find("#") < 0 and line.find("=") > -1 :
                if len(line) > 1 :
                        paramsList = line.rstrip().split("= ")
                        key = paramsList[0].replace("\t","")
                        #print(len(paramsList), paramsList)
                        if len(paramsList) > 1  :
                            paramHash[key] = paramsList[1]
                        else:
                            paramHash[key] = ""
    #saveJson(paramHash,"./tilesParams.json")
    return paramHash
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
def saveJson(Json,fileName):
    start_time = time.time()
        ##replace here as overflow when writing
        #with gzip.open(fileName,"w") as fout:
        #    json_str = json.dumps(Json,indent=1) + "\n"
        #    json_bytes = json_str.encode('utf-8')
        #    fout.write(json_bytes)

    with open(fileName, 'w') as fp:
        json.dump(Json, fp, indent=1)
    if fileName.split(".")[-1] == "gz":
        newFileName = fileName.replace(".gz","")
        os.system("mv "+ fileName + " " + newFileName)
        os.system("gzip " + newFileName)

    print ("\t SaveJson  :", fileName, ":", int(time.time() - start_time), "S")
def loadJson(fileName):
    # open JSON file and parse contents
    #print ("Lading json",fileName)
    if os.path.isfile(fileName):
        start_time = time.time()
        if fileName.split(".")[-1] == "gz":
            with gzip.open(fileName, "rt") as fin:
                json_str = fin.read()
                data = json.loads(json_str)
        else:
            with open(fileName,'r') as fin:
                data = json.load(fin)
        print("\t LoadJson  :", fileName, ":", int(time.time() - start_time), "S")
    else:
        print("Missing Json file", fileName)
        data = {}
    return data
def patternMatch(pattern,target_string):
    print  (target_string,pattern)
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
        elif len(pinAttr) == 2 :
            attrKey = pinAttr[0]
            attrVal = pinAttr[1]
            pinHash[pinName][attrKey] =attrVal
        #elif re.match("LAYER", pinAttr[0]) > 0:
        #    j = j + 1
        #   termName = 'term_' + str(j)
        #    result = patternMatch(icVar.portShape,pinList[i])
            #print pinName,termName
            #pinHash[pinName][termName] = {}
            #pinHash[pinName][termName]["LAYER"] = result[0][0][1]
            #pinHash[pinName][termName]["SHAPE"] = result[0][0][2]
        #elif re.match("UNPLACED",pinAttr[0]) > 0:
        #    result = patternMatch(icVar.portStatus, pinList[i])
        #   pinHash[pinName][termName]["status"] = result[0][0][0]
        #elif re.match("PLACED|FIXED|COVER",pinAttr[0]) > 0:
        #    result = patternMatch(icVar.portStatus,pinList[i])
        #    pinHash[pinName][termName]["status"] = result[0][0][0]
        #    pinHash[pinName][termName]["LOCATION"] = result[0][0][1]
        #    pinHash[pinName][termName]["oritation"] = result[0][0][2]
    return  pinHash
def comp2dict(comp,dbu):
    compHash = {}
    compList = comp.split("+")
    instName,refname = compList[0].split()[1:3]
    instName.replace("\\\\","")

    if re.search("|".join(["_FILL","_DCAP","_TAP","_CAP","PDF_DFI"]),refname):
        return compHash
    else:
        compHash[instName] = {}
        compHash[instName]["refname"] = refname
        # print icVar.placeStatus, type(icVar.placeStatus)
        for i in range(1,len(compList)):
            attrList = compList[i].split()
            if attrList[0] == "UNPLACED":
                compHash[instName]["status"] = "UNPLACED"
            elif re.search("PLACED|FIXED|COVER",attrList[0]) :
                # print icVar.rePlaceStatus.search(compItem), compItem.find("PLACED"), compItem
                # print compItem
                compHash[instName]["status"] = attrList[0]
                compHash[instName]["llx"] = float(attrList[2]) /dbu
                compHash[instName]["lly"] = float(attrList[3]) /dbu
                compHash[instName]["oritation"] = attrList[5]
            #if attrList[0] == "SOURCE":
            #    compHash[instName]["SOURCE"] = attrList[1]
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
            netHash[netName]["pin"] = []
        elif len(pinList) == 2:
            netHash[netName]["pin"].append("/".join(pinList))
        #else:
        #   print pinList
    for i in range(1,len(itemList)):
        attrList = itemList[i].split()
        if attrList[0].find("USE") > -1 :
            netHash[netName]["USE"] = attrList[1]
        elif attrList[0].find("NONDEFAULTRULE") > -1:
            netHash[netName]["NONDEFAULTRULE"] = attrList[1]
        elif  re.search(r"(ROUTED|FIXED|SHAPE|MASK|RECT)",attrList[0]):
            skip = 0
        #else:
            #print "New attr", attrList[0]
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
    module=module.replace("\\","")
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
        #print "Port dir: ", port
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
                        moduleHash[moduleName]["NET"][portName]["PINS"] = []
                    else:
                        moduleHash[moduleName]["PORT"][portName]["dir"] = dir
                        moduleHash[moduleName]["PORT"][portName]["WIDTH"] = busWidth

                        moduleHash[moduleName]["NET"][portName] = {}
                        moduleHash[moduleName]["NET"][portName]["PINS"] = portName
            else:
                #print "Parsing input Signal", item
                for portName in itemP.split()[1:]:
                    portName = portName.rstrip()
                    #print "PortName", portName, attr,dir
                    if attr == "NET":
                        moduleHash[moduleName]["NET"][portName] = {}
                        moduleHash[moduleName]["NET"][portName]["PINS"] = []
                    else:
                        moduleHash[moduleName]["PORT"][portName] = {}
                        moduleHash[moduleName]["PORT"][portName]["dir"] = dir
                        moduleHash[moduleName]["PORT"][portName]["WIDTH"] = 0
                        moduleHash[moduleName]["NET"][portName] = {}
                        moduleHash[moduleName]["NET"][portName]["PINS"] = []
                        moduleHash[moduleName]["NET"][portName]["PINS"].append(portName)
        else :
            ## instance/module instantial
            #print item
            inst = reInstVlg.match(item)
            if inst:
                refname = inst.group(1)
                instName = inst.group(2)
                moduleHash[moduleName]["INST"][instName] = {}
                moduleHash[moduleName]["INST"][instName]["pin"] = {}
                moduleHash[moduleName]["INST"][instName]["refname"] = refname
                pins = inst.group(3)
                #print refname,instName
                for pn in pins.split(".")[1:]:
                    pl = re.split("[\(\)\,]",pn)
                    pin, net = pl[0],pl[1]
                    #print "\t", pin ,net
                    moduleHash[moduleName]["INST"][instName]["pin"][pin] = net
                    if net == "1\'b0": net = "TIEL"
                    if net == "1\'b1": net = "TIEH"
                    if net.find("\.") > -1:
                        print("pinBus", net)
                    else:

                        if net in moduleHash[moduleName]["NET"]:
                            moduleHash[moduleName]["NET"][net]["PINS"].append(instName+"/"+pin)
                        else:
                            moduleHash[moduleName]["NET"][net] = {}
                            moduleHash[moduleName]["NET"][net]["PINS"] = []
                            moduleHash[moduleName]["NET"][net]["PINS"].append(instName+"/"+pin)
    return moduleHash
def instrefname(moduleHash,instName):
    topName = moduleHash["TOP"]
    hierNameList = instName.split("/")

    if hierNameList[0] in moduleHash[topName]["INST"]:
        refname = moduleHash[topName]["INST"][hierNameList[0]]["refname"]
        print("debug: ", hierNameList[0])
        if moduleHash[topName]["INST"][hierNameList[0]]["isLeaf"] == 1:
            return refname
        else:
            for moduleName in hierNameList[1:-1]:
                refname = moduleHash[refname]["INST"][moduleName]["refname"]
            return refname
    else:
        print("Not found inst", instName)
        return "ERROR"
def rename(self,key,newKey):
    ind = self._keys.index(key)
    self._keys[ind] = newKey
    self[newKey] = self[key]
    self._keys.pop(-1)
def flatModule(moduleHash,topName):
    print("Getting Flat Cells")
    flatCellsHash = {}
    hierName = []
    def subModuleCells(moduleHash,moduleName):
        #print "flatten module", moduleName
        subFlatHash = {}
        for instName in moduleHash[moduleName]["INST"]:
            refname = moduleHash[moduleName]["INST"][instName]["refname"]

            if refname not in moduleHash:
                subFlatHash[instName] = moduleHash[moduleName]["INST"][instName]
            else:
                hierCells = subModuleCells(moduleHash,refname)
                #newFlatCells = map(lambda x: instName+"/"+x,hierCells)
                for key in hierCells:
                    newKey = instName+"/"+key
                    subFlatHash[newKey] = hierCells[key]
                #subFlatHash.update(newFlatCells)
        return subFlatHash

    for instName in moduleHash[topName]["INST"]:
        refname = moduleHash[topName]["INST"][instName]["refname"]
        if refname in moduleHash:
            ## find submodule instance with prefix instName
            hierCells = subModuleCells(moduleHash, refname)
            # newHierCell = map(lambda x: instName+"/"+x,hierCell)
            # print "hierCells type", type(hierCells)
            for key in hierCells:
                #flatCellsHash[instName + "/" + key] = hierCells[key].copy()
                newKey = instName + "/" + key
                flatCellsHash[newKey] = hierCells[key]
        else:
            flatCellsHash[instName] = moduleHash[topName]["INST"][instName]
    return flatCellsHash
def lef2hash(lefFile):
    ##read lef file , return the hash with macro nanme key
    lefHash = {}
    if os.path.isfile(lefFile):
        if lefFile.split(".")[-1] == "gz":
            fp = gzip.open(lefFile,"rt")
        else:
            fp = open(lefFile,"rt")
        #print "lef2hash ", lefFile
        #print(lefFile,type(fp))
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
                    elif line1.find(" SIZE ") > -1:

                        lefHash[macroName]["width"]  = float(line1.split()[1])
                        lefHash[macroName]["height"] = float(line1.split()[3])

                    elif line1.find("PIN ") > -1:
                        pinName = line1.split()[1]
                        # print "pin ",macroName, pinName
                        lefHash[macroName]["pin"] = {}
                        lefHash[macroName]["pin"][pinName] = {}
                        ##parsing PIN section
                        for line2 in fp:
                            # print "in pin",line2
                            if line2.find("END") > -1:
                                break
                            elif line2.find("DIRECTION") > -1:
                                lefHash[macroName]["pin"][pinName]["dir"] = line2.split()[1]
                            elif line2.find("USE") > -1:
                                lefHash[macroName]["pin"][pinName]["use"] = line2.split()[1]
                            #elif line2.find("SHAPE") > -1:
                            #    lefHash[macroName]["pin"][pinName]["SHAPE"] = line2.split()[1]
                            #elif line2.find("ANTENNA") > -1:
                            #    antKey, antValue = line2.split()[0], line2.split()[1:-1]
                            #    lefHash[macroName]["pin"][pinName][antKey] = antValue

                            #ignored pin shape imformation as no request
                            #elif line2.find("PORT") > -1:
                            #    i = 0
                            #    # parsing PORT section
                            #    for line3 in fp:
                            #        # print "in port",line3
                            #        if line3.find("END") > -1:
                            #            break
                            #        elif line3.find("LAYER") > -1:
                            #            layerName = line3.split()[1]
                            #            # print layerName
                            #            #lefHash[macroName]["pin"][pinName]["layer"] = layerName
                            #        elif line3.find("RECT") > -1:
                            #            # print "rect line", line3 ,i, type(lefHash["MACRO"][macroName]["pin"][pinName]["PORT"][layerName] )
                            #            lefHash[macroName]["pin"][pinName]["llx"],lefHash[macroName]["pin"][pinName]["lly"] = line3.split()[-3:-1]
                            #            l = line3.split()[2]
                            #        #elif line3.find("POLYGON") > -1:
                            #        #    lefHash[macroName]["pin"][pinName]["PORT"][layerName][
                            #        #        i] = line3.split()[1:-1]
                            #        #    i = i + 1
                            #        #else:
                            #        #    print "Found incorrect Keyword", line3, lefFile, fp.filelineno()
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
        fp.close()
    else :
        #print"missed file ", lefFile
        print("missed file ", lefFile)
    return lefHash
def def2hash(defFile):
    dsgHash = {}
    dsgHash["FP"] = {}
    dsgHash["INST"] = {}
    dsgHash["NET"] = {}
    dsgHash["PORT"] = {}
    allItem = []
    singleItem = []

    skipNets = 1
    skipSNets = 1
    skipComp = 0
    skipPin = 1
    skipBkg = 1
    ## skipped as new format not recgnize
    skipVia = 1
    if os.path.isfile(defFile):
        if defFile.split(".")[-1] == "gz":
            fp = gzip.open(defFile, "rt")
        else:
            fp = open(defFile, "rt")
        print("def2Json :", defFile)
        for line0 in fp:
            if line0.find('PINS') == 0 and skipPin == 0 :
                for line1 in fp:
                    if line1.find('END PINS') == 0:
                        if "PORT" not in dsgHash: dsgHash["PORT"] = {}
                        print("\tParsing PINS")
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
                        print("\tParsing COMPONENT")
                        if "INST" not in dsgHash: dsgHash["INST"] = {}
                        for i in range(len(allItem)):
                            dsgHash["INST"].update(comp2dict(allItem[i], dsgHash["FP"]["DBU"]))
                        allItem = []
                        singleItem = []
                        return dsgHash
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
                        print("\tParsing BLOCKAGE")
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
                        print("\tParsing VIAS")
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
                        print("\tParsing NETS")
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
                        print ("\tParsing SPECIALNETS")

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
            elif line0.find("UNITS DISTANCE MICRONS") == 0:
                dsgHash["FP"]["DBU"] = float(line0.split()[3])
                #print(dsgHash["FP"]["DBU"])
                #exit()

        fp.close()
    else:
        print("missed def file",defFile)
    return dsgHash
def vlg2hash(vlgFile):
    moduleHierHash = {}
    print ("verilog2json", vlgFile)
    fp = fi.FileInput(vlgFile, openhook=fi.hook_compressed)
    for line0 in fp:
        if line0.find("module ") == 0:
            moduleCont = ""
            moduleCont += line0.strip()
            for line1 in fp:
                if line1.find("endmodule") == 0:
                    # print "module", allItem
                    moduleHierHash.update(module2dict(moduleCont))
                    break
                else:
                    moduleCont += line1.strip()
    fp.close()
    return moduleHierHash
def i2NetEst2Hash(iccNetEst):
    localHash = {}
    if os.path.isfile(iccNetEst):
        print ("iccNetEst2Hash", iccNetEst)
        fp = fi.FileInput(iccNetEst, openhook=fi.hook_compressed)
        for line0 in fp:
            if line0.find("the length of net") > -1:
                netName, netLen = line0.split()[4], line0.split()[6]
                localHash[netName]["ESTLEN"] = netLen
        fp.close()
    else:
        print ("iccNetEst2Hash missed ", iccNetEst)
    return localHash
def i2NetPhy2Hash(i2NetPhy):
    localHash = {}
    if os.path.isfile(iccNetPhy):
        start_time = time.time()
        print ("i2NetPhy to Hash", iccNetPhy)
        fp = fi.FileInput(iccNetPhy, openhook=fi.hook_compressed)
        for line0 in fp:
            if line0.find("flat_net") > -1:
                netName = line0.split()[1]
                for line1 in fp:
                    if line1.find("route_length") > -1:
                        localHash[netName]["PHYLEN"] = line1.strip()
                        break
        print ("\t runtime :", time.time() - start_time, "S")
        fp.close()
    else:
        print ("i2NetPhy to Hash missed ", iccNetPhy)
    return localHash
def tile2top(tileJsonFile, mpuJsonFile,libJsonFile):
    return 0
def cellDelay(iTran, oLoad,cellName, fromPin, toPin):
    return 0
def libBom2Json(libBomFile,jsonOut):
    libBom = Bom(libBomFile)
    libBomHash = loadJson(libBomFile)
    libHash = {}

    for ips in libBomHash["ips"]:
        #print ips
        if libBomHash["ips"][ips]["iptype"] == "tech":
            libHash["tech"] = {}
        else:
            #libHash["stdcel"] ={}
            for libName in ips.split(","):
                for item in  libBom.find_designfiles(filetype='lib',ipname=libName):
                   libFile = item.get_filename()
                   ipname  = item.get_ipname()
                   corner  = item.get_corner().name()
                   if corner not in libHash:
                       libHash[corner]= {}
                   else:
                        #print "lib ",corner, ipname, libFile
                        libHash[corner].update(lib2hash(libFile))
    saveJson(libHash,jsonOut+"libs.json.gz")


    lefHash = {}

    for item in  libBom.find_designfiles(filetype='lef'):
        lefFile = item.get_filename()
        ipname = item.get_ipname()
        lefHash.update(lef2hash(lefFile))
    saveJson(lefHash,jsonOut + "lefs.json.gz")
def fctBom2Json(fctBomFile,jsonOut,topName):
    print("Building DB from Bom", fctBomFile)
    fctBomHash = Bom(fctBomFile)
    tileLefHash= {}

    for item in fctBomHash.find_designfiles(filetype='lef'):
        tileName = item.get_ipname()
        lefFile = item.get_filename()
        # print lefFile, tileName
        tileLefHash.update(lef2hash(lefFile))
    saveJson(tileLefHash, jsonOut + "tilesLef.json.gz")
    tileLefHash = {}
    # load tiop cell at first
    topHash = {}


    topDefFile = fctBomHash.find_designfiles(filetype='def',abstract="glassbox" ,ipname=topName)[0].get_filename()
    topHash = def2hash(topDefFile)
    print ("loading ", topDefFile)
    saveJson(topHash, jsonOut + topName+".only.inst.json.gz")

    tileHash = {}
    for item in fctBomHash.find_designfiles(filetype='def',abstract="greybox"):
        tileName = item.get_ipname()
        defFile  = item.get_filename()
        print ("loading ", defFile)
        tileHash[tileName] = def2hash(defFile)
        #saveJson(tileHash[tileName],jsonOut+tileName+".design.json")
    saveJson(tileHash, jsonOut + "tiles.inst.json.gz")


    #read verilog is commited , as tech issue
    '''
    #topVlgFile = fctBomHash.find_designfiles(filetype='verilog',abstract='glassbox' ,ipname=topName)[0].get_filename()
    #topVlgHash = vlg2hash(topVlgFile)
    #saveJson(topVlgHash,jsonOut+topName+".vlg.json")
    
    vlgIlmHash = {}
    for item in fctBomHash.find_designfiles(filetype='verilog',abstract="greybox",attrs="max",extract="typrc100c",libcorner="tt0p65v0c",sdc_mode="FuncTT0p65v"):
        tileName = item.get_ipname()
        vlgFile  = item.get_filename()
        print ("loading ", vlgFile)
        vlgIlmHash[tileName] = vlg2hash(vlgFile)
        saveJson(vlgIlmHash[tileName],jsonOut+tileName+".vlg.json")
    saveJson(tileVlgHash, jsonOut + "tiles.vlg.json")

    for item in fctBomHash.find_designfiles(filetype='verilog',abstract="greybox",attrs="max",extract="typrc100c",libcorner="tt0p65v0c",sdc_mode="FuncTT0p65v"):
        tileName = item.get_ipname()
        vlgIlmHash.update(loadJson(jsonOut + tileName+ ".vlg.json"))
    vlgIlmHash.update(loadJson(jsonOut + "mpu.vlg.json"))

    flatVlgHash = flatModule(vlgIlmHash,topName)
    saveJson(flatVlgHash,jsonOut + "mpu.flat.vlg.json")
    '''
    #topOnlyHash  = loadJson(jsonOut+topName+".only.inst.json.gz")
    #tileHash     = loadJson(jsonOut+"tiles.inst.json.gz")
    topFlatHash = flatTopTile(topHash,tileHash)
    #saveJson(topFlatHash,jsonOut + topName+".inst.json.gz")
    tileHash = {}
    topHash = {}

    topHash = readSlackTable("./data/slackTable.rpt.gz")
    topHash["INST"] = topFlatHash["INST"]
    topFlatHash = {}

    #saveJson(topHash, jsonOut + topName + ".json")
    saveJson(topHash["INST"], jsonOut + topName + ".inst.json")
    saveJson(topHash["NET"] , jsonOut + topName + ".net.json")
    saveJson(topHash["PIN"] , jsonOut + topName + ".pin.json")

    return topHash
def flatTopTile(topHash,tileHash):
    topHashFlat = copy.deepcopy(topHash)
    for topInst in topHash["INST"]:
        if topHash["INST"][topInst]["refname"] in tileHash:
            tileName = topHash["INST"][topInst]["refname"]
            #print "tileName ", tileName
            for tileInst in tileHash[tileName]["INST"]:
                flatInst = topInst + "/" +  tileInst
                #print("addinng  flat inst", flatInst)
                topHashFlat["INST"][flatInst] = {}
                topHashFlat["INST"][flatInst]["refname"] =  topHash["INST"][topInst]["refname"]
                if   topHash["INST"][topInst]["oritation"] == "N":
                    topHashFlat["INST"][flatInst]["llx"] = topHash["INST"][topInst]["llx"] + tileHash[tileName]["INST"][tileInst]["llx"]
                    topHashFlat["INST"][flatInst]["lly"] = topHash["INST"][topInst]["lly"] + tileHash[tileName]["INST"][tileInst]["lly"]
                elif topHash["INST"][topInst]["oritation"] ==  "S":
                    topHashFlat["INST"][flatInst]["llx"] = topHash["INST"][topInst]["llx"] - tileHash[tileName]["INST"][tileInst]["llx"]
                    topHashFlat["INST"][flatInst]["lly"] = topHash["INST"][topInst]["lly"] - tileHash[tileName]["INST"][tileInst]["lly"]
                elif topHash["INST"][topInst]["oritation"] == "W":
                    topHashFlat["INST"][flatInst]["llx"] = topHash["INST"][topInst]["llx"] - tileHash[tileName]["INST"][tileInst]["lly"]
                    topHashFlat["INST"][flatInst]["lly"] = topHash["INST"][topInst]["lly"] + tileHash[tileName]["INST"][tileInst]["llx"]
                elif topHash["INST"][topInst]["oritation"] == "E":
                    topHashFlat["INST"][flatInst]["llx"] = topHash["INST"][topInst]["llx"] + tileHash[tileName]["INST"][tileInst]["lly"]
                    topHashFlat["INST"][flatInst]["lly"] = topHash["INST"][topInst]["lly"] - tileHash[tileName]["INST"][tileInst]["llx"]
                elif topHash["INST"][topInst]["oritation"] == "FN":
                    topHashFlat["INST"][flatInst]["llx"] = topHash["INST"][topInst]["llx"] - tileHash[tileName]["INST"][tileInst]["llx"]
                    topHashFlat["INST"][flatInst]["lly"] = topHash["INST"][topInst]["lly"] - tileHash[tileName]["INST"][tileInst]["lly"]
                elif topHash["INST"][topInst]["oritation"] == "FS":
                    topHashFlat["INST"][flatInst]["llx"] = topHash["INST"][topInst]["llx"] + tileHash[tileName]["INST"][tileInst]["llx"]
                    topHashFlat["INST"][flatInst]["lly"] = topHash["INST"][topInst]["lly"] - tileHash[tileName]["INST"][tileInst]["lly"]
                elif topHash["INST"][topInst]["oritation"] == "FW":
                    topHashFlat["INST"][flatInst]["llx"] = topHash["INST"][topInst]["llx"] + tileHash[tileName]["INST"][tileInst]["lly"]
                    topHashFlat["INST"][flatInst]["lly"] = topHash["INST"][topInst]["lly"] + tileHash[tileName]["INST"][tileInst]["llx"]
                elif topHash["INST"][topInst]["oritation"] == "FE":
                    topHashFlat["INST"][flatInst]["llx"] = topHash["INST"][topInst]["llx"] - tileHash[tileName]["INST"][tileInst]["lly"]
                    topHashFlat["INST"][flatInst]["lly"] = topHash["INST"][topInst]["lly"] - tileHash[tileName]["INST"][tileInst]["llx"]
                else:
                    #print "Bad orirentation", topHash["INST"][topInst]["oritation"]
                    empty = 0
            #for tileNet in tileHash[tileName]["NET"]:
            #    flatNet = topInst + "/" + tileNet
    return topHashFlat
def lib2hash(libFile):
    libHash = {}
    braceCounter = 0
    if os.path.isfile(libFile):
        with gzip.open(libFile,"rt") as fp:
            print ("lib2hash ", libFile)
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
        print ("miss libFile ",libFile)
    return libHash
def readSlackTable(slackTableFile):

    topHash = {}
    topHash["NET"] = {}
    topHash["PIN"] = {}
    topHash["INST"] = {}
    start_time = time.time()


    with gzip.open(slackTableFile,"rt") as fp:
        for line0 in fp:
            if line0.find("#") < 0 :
                for line1 in fp:

                    items = line1.replace("NA","0").replace("INFINITY","100000").split()
                    #print len(items), line1,
                    #print items
                    if len(items) == 8:
                        pinName,netName,fSlack,rSlack,fTran,rTran,fCeff,rCeff =items[0:8]
                        pinName = pinName.replace(":","/")
                        topHash["PIN"][pinName] = {}
                        topHash["PIN"][pinName]["Slack"] = min(float(fSlack),float(rSlack))
                        #topHash["PIN"][pinName]["rSlack"] = rSlack
                        topHash["PIN"][pinName]["Tran"]  = max(float(fTran),float(rTran))
                        #topHash["PIN"][pinName]["rTran"]  = rTran
                        topHash["PIN"][pinName]["Cap"]  = max(float(fCeff),float(rCeff))
                        #topHash["PIN"][pinName]["rCap"]  = rCeff
                        topHash["PIN"][pinName]["net"] = netName
                        try :
                            topHash["NET"][netName]["pin"].append(pinName)
                        except KeyError:
                            topHash["NET"][netName] = {}
                            topHash["NET"][netName]["pin"] =  []
                            topHash["NET"][netName]["pin"].append(pinName)

                        #instName = pinName.split(":")[0]
                        #if instName not in topHash["INST"]:
                        #    topHash["INST"][instName] = {}

    print ("\t Loading SlackTable :", int(time.time() - start_time), "S")
    return topHash
                #print pinName,top_net_name,worst_fall_slack,worst_rise_slack,max_fall_er,max_rise_er,max_fall_ceff,max_rise_ceff
                #print line1.split()
                #exit()
def receiveAll(s):

    dataAll = ""
    i = 0
    data = s.recv(4096).decode()
    print(dataAll, i, data.find("DONE"))
    while data.find("DONE") == 0  and i < 5:
        dataAll += data
        data = s.recv(4096).decode()
        i += 1
        print(dataAll, i, data.find("DONE"))
    return dataAll
def recvEnd(theSocket):
    END = "DONE"
    totalData = [];
    data = ""
    while True:
        data=theSocket.recv(8192).decode()
        print(data)
        if END in data:
            totalData.append(data[:data.find(END)])
            break
        totalData.append(data)

        if len(totalData) > 1:
            lastPair = totalData[-2]+totalData[-1]
            if END in lastPair:
                totalData[-2] = lastPair[:lastPair.find(END)]
                totalData.pop()
                break
    #return ''.join(totalData)
    return totalData
def report_timing( ):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with open("/home/yaguo/zoo/eda2json/ptServer", "r") as fp:
        ip, port = fp.readline().rstrip().split()
        server = (ip, int(port))
        s.connect(server)
        cmd = b"report_timing "
        s.sendall(cmd)
        allData = recvEnd(s)
        s.close
        return allData
def pt_shell():

    print("Enter Pt mode, enjoy.")

    while True:
       try:
           cmd = input("\npt_shell->")
           if cmd.find("exit") > -1:
               return 0
           else :
               s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
               with open("./data/ptserver.list", "r") as fp:
                   nickName ,targetName, ip, port = fp.readline().rstrip().split()
                   server = (ip, int(port))
                   s.connect(server)
                   s.sendall(cmd.encode())
                   allData = recvEnd(s)
                   s.close
                   #print(allData)
       except ValueError:
           print("wrong command")
def clkTranRpt2json ():

    for clkTran in glob.glob(rundir + "rpts/PtDrv*/clock_trans.rpt.gz"):
        print("Reading clock tran report", clkTran)
        scenarios = re.split("\/", clkTran)
        # print type(scenarios),len(scenarios),type(clkTran),scenarios
        scenario = scenarios[-2]
        fp = fi.FileInput(clkTran, openhook=fi.hook_compressed)
        clkTranHash = {}
        for line0 in fp:
            # print line0
            if line0.find("Net:") == 0:
                netName = line0.split()[1]
                #print "netName", netName
                clkTranHash[netName] = {}
                clkTranHash[netName][scenario] = {}
                clkTranHash[netName][scenario]["Sink"] = []
                for line1 in fp:
                    if line1.find(" ;") == 0:
                        break
                    elif line1.find("Slack:") > -1:
                        clkTranHash[netName][scenario]["Slack"] = float(line1.split()[-1])
                    elif line1.find("Value") > -1:
                        clkTranHash[netName][scenario]["Value"] = float(line1.split()[-1])
                    elif line1.find("Limit") > -1:
                        clkTranHash[netName][scenario]["Limit"] = float(line1.split()[-1])
                    elif line1.find("CLOCK") > -1:
                        clkTranHash[netName][scenario]["CLOCK"] = float(line1.split()[-1])
                    elif line1.find("Driver") > -1:
                        driver = line1.split()[1]
                        refName = line1.split()[-1]
                        refName = re.sub(r'[\(|\)]', "", refName)
                        line2 = fp.readline()
                        slew  = line2.split()[-1]
                        clkTranHash[netName][scenario]["DRIVER"]  = []
                        clkTranHash[netName][scenario]["DRIVER"].append([driver, refName,slew])
                        clkTranHash[netName][scenario]["SINK"] =  []
                    elif line1.find("Sink") > -1:
                        sink = line1.split()[1]
                        refName = line1.split()[-1]
                        refName = re.sub(r'[\(|\)]', "", refName)
                        line2 = fp.readline()
                        slew = line2.split()[-1]
                        clkTranHash[netName][scenario]["SINK"].append([sink, refName,slew])
        fp.close()
    with open('clkTrans.json', 'w') as fp:
        json.dump(clkTranHash, fp, indent=1)
    fp.close()
def fixCTrans(dsgHash,libHash,rptHash,ecoFile):
    for net in rptHash:
        for sce in rptHash[net]:
            driver, driverRef, driverSlew =  rptHash[net][sce]["DRIVER"][0]
            driveStrength = driverRef.split("_")[-1]
            driverInst = driver.split("\/")[0:-1].join("\/")
            value =  rptHash[net][sce]["Value"]
            limit =  rptHash[net][sce]["Limit"]
            sinkNum = len(rptHash[net][sce]["Sink"])
            print(driver,driverInst, driverRef, driverSlew, value ,limit, driveStrength)
            if driverSlew / limit > 0.8:
                print("insert_buffer_on_route -net [get_nets -of [get_pins", driverRef, "/CLK]]")
            elif driveStrength < 6:
                print("size_cell ",driverInst,"HDBLVT08_BUF_CK_8")
            elif sinkNum > 3:
                # check the mahantten distance
                sink1CelLoc = rptHash[net][sce]["Sink"][0]
def compareDef (refDef, tarDef, ecoFile):
    refDefHash = load_json(refDef)
    tarDefHash = load_json(tarDef)
    diffHash = {}
    diffHash["CHANGE"] = {}
    diffHash["ADD"] = {}
    for dict_key in refDefHash.keys():
        if dict_key not in tarDefHash:
            diffHash["ADD"][dict_key] = tarDefHash[dict_key]
        elif compareJson(refDefHash[dict_key],tarDefHash[dict_key]) == False:
                diffHash["CHANGE"][dict_key] = tarDefHash[dict_key]
    for dict_key in tarDefHash.keys():
        if dict_key not in refDefHash:
            diffHash["DEL"][dict_key] = tarDefHash[dict_key]

    with open('./json/diff.json', 'w') as JsonFP:
        json.dump(diffHash, JsonFP, indent=1)

    json2def("./json/diff.json",ecoFile)
def json2def(jsonFile, ecoFile):
    #support componets only

    tile = """VERSION 5.7 ;
DIVIDERCHAR "/" ;
BUSBITCHARS "[]" ;
DESIGN smu_zcn1_t ;
UNITS DISTANCE MICRONS 2000 ;
COMPONENTS 100 ; """
    defHash = load_json(jsonFile)

    with open(ecoFile,"w") as fp:

        fp.writelines(tile + "\n")
        for dict_key in defHash.keys():
            if dict_key == "ADD":
                print("not suport add cell")
            elif dict_key == "CHANGE":
                for instName in defHash[dict_key].keys():
                    setStatus = "set_placement_status placed [get_flat_cell  "+ instName + " ]"
                    location = " ".join(defHash[dict_key][instName]["LOCATION"])
                    #print "oritation: ", type(defHash[dict_key][instName]["ORITATION"])
                    #print "instName:", type(instName)
                    defLine = " - " + instName + " " +  defHash[dict_key][instName]["REFNAME"]  + \
                              " + " +  defHash[dict_key][instName]["STATUS"] +  \
                              " ( " + location + " ) " + defHash[dict_key][instName]["ORITATION"] + " ;"
                    #setRef    = "size_cell "+ instName + defHash[dict_key][instName]["REFNAME"]
                    #setLocation = "move_object [get_flat_cell" + instName + "]" + "-to" + "{" + +"}"
                    #setLocation = "move_object [get_flat_cell " + instName + "]" + " -to" + " { "  + location + " } "
                    fp.writelines(defLine + "\n" )
                    #fp.writelines(defHash[dict_key][instName]["LOCATION"])

                    #fp.write(setRef)
                    #fp.write(setLocation + "\n")
        fp.writelines("END COMPONENTS" + "\n" + "END DESIGN" + "\n")
def json2eco(jsonFile, ecoFile):
    #support componets only
    defHash = load_json(jsonFile)
    with open(ecoFile,"w") as fp:
        for dict_key in defHash.keys():
            if dict_key == "ADD":
                print("not suport add cell")
            elif dict_key == "CHANGE":
                for instName in defHash[dict_key].keys():
                    setStatus = "set_placement_status placed [get_flat_cell  "+ instName + " ]"
                    location = " ".join(defHash[dict_key][instName]["LOCATION"])
                    #setRef    = "size_cell "+ instName + defHash[dict_key][instName]["REFNAME"]
                    #setLocation = "move_object [get_flat_cell" + instName + "]" + "-to" + "{" + +"}"
                    setLocation = "move_object [get_flat_cell " + instName + "]" + " -to" + " { "  + location + " } "
                    fp.writelines(setStatus + "\n" )
                    #fp.writelines(defHash[dict_key][instName]["LOCATION"])

                    #fp.write(setRef)
                    fp.write(setLocation + "\n")
def compareJson(data_a,data_b):
    # type: list
	if (type(data_a) is list):
		# is [data_b] a list and of same length as [data_a]?
		if (
			(type(data_b) != list) or
			(len(data_a) != len(data_b))
		):
			return False

		# iterate over list items
		for list_index,list_item in enumerate(data_a):
			# compare [data_a] list item against [data_b] at index
			if (not compareJson(list_item,data_b[list_index])):
				return False

		# list identical
		return True

	# type: dictionary
	if (type(data_a) is dict):
		# is [data_b] a dictionary?
		if (type(data_b) != dict):
			return False

		# iterate over dictionary keys
		for dict_key,dict_value in data_a.items():
			# key exists in [data_b] dictionary, and same value?
			if (
				(dict_key not in data_b) or
				(not compareJson(dict_value,data_b[dict_key]))
			):
				return False

		# dictionary identical
		return True

	# simple value - compare both value and type for equality
	return (
		(data_a == data_b) and
		(type(data_a) is type(data_b))
	)
def fixDeltaTrans(rundir):
    netList = []
    rpt = rundir + "rpts/SortHldEcoRouteFuncFFG1p05vffg1p05v0cEcoRouteSxGrp/H.INTERNAL.sorted.gz"
    ecoFile = rundir + "data/deltaTrans.eco"
    fp = fi.FileInput(rpt, openhook=fi.hook_compressed)
    for line1 in fp:
        if line1.find("(net)") > 0:
            netAttr = line1.split()
            if len(netAttr) > 3:
                netName = netAttr[0]
                netFanout = netAttr[2]
                netCap = float(netAttr[3])
                if netCap > 8:
                    for line2 in fp:
                        flatPinList = line2.split()
                        if len(flatPinList) == 9:
                            deltaTrans = float(flatPinList[2])
                            if deltaTrans < -10 :
                                #print "debug", netName,deltaTrans,flatPinList[1]
                                #print line2
                                netList.append(netName)
                            break

    #                print line1
    bufCell = "HDBLVT08_BUF_4"
    preFix = "yaguo_1029_deltaTrans"
    netList =list(set(netList))
    #with open(ecoFile,"w") as fpw:
    #    for net in netList:
    #            fpw.write("catch { add_buffer_on_route "+ net + " -lib_cell " + bufCell +  " -net_prefix " + preFix + " -cell_prefix " + preFix + " -repeater_distance 40 -no_legalize -punch_port -verbose}\n")
    return netList
def fixSiHold():
    pinList = []
    rpt = rundir + "rpts/SortHldEcoRouteFuncFFG1p05vffg1p05v0cEcoRouteSxGrp/H.INTERNAL.sorted.gz"
    fp = fi.FileInput(rpt, openhook=fi.hook_compressed)
    for line1 in fp:
        flatPinLine = line1.split()
        if len(flatPinLine) == 9 :
            endPoint =  flatPinLine[0]
            line2 = fp.readline()
            if line2.find("data arrival time") > -1:
                #print "endpoint:", endPoint
                pinList.append(endPoint)

    bufCell = "HDBLVT08_BUF_1"
    preFix = "yaguo_1030_holdFix"
    i2Eco = open(rundir + "/data/holdfix.i2.eco","w")
    ptEco = open(rundir + "/data/holdfix.pt.eco", "w")
    for pin in pinList:
        i2Eco.write("catch { buffer_pin "+ pin + " " + bufCell + " " + preFix + " }\n")
        ptEco.write("catch { insert_buffer " + pin + " " + bufCell + " }\n")
def fixDrv(rundir):
    dwRpt = rundir + "mis_checks/double_switch.txt"
    dtRpt = rundir + "mis_checks/data_trans.txt"
    sibRpt = rundir  + "mis_checks/si_bottleneck.txt"
    glhRpt = rundir + "mis_checks/glitch.txt"
    allRpt = glob.glob(rundir+"mis_checks/"+"*")
    #fpw = open(rundir + "data/drvFix.eco", "w")
    drvNetList = []
    for rpt in allRpt:
        if re.search(r"double_switch",rpt):
            print("open ", rpt)
            with open(rpt,"r") as fp :
                for line1 in fp:
                    net = line1.split()[0]
                    drvNetList.append(net)
            print("drvnet1 count", len(drvNetList))
        elif re.search(r"data_trans",rpt):
            print("open ", rpt)
            i2Eco = open(rundir + "/data/dtran.i2.eco", "w")
            with open(rpt, "r") as fp:
                for line1 in fp:
                    #print line1.split()
                    net,driver,refName = line1.split()[0:3]
                    drvNetList.append(net)
                    bufCell = "HDBLVT08_BUF_8"
                    preFix = "yaguo_1101_dtranFix"
                    #i2Eco.write(" buffer_pin " + driver + " " + bufCell + " " + preFix + " \n")
            print("drvnet1 count", len(drvNetList))

        elif re.search(r'si_bottleneck|glitch',rpt):
            print("open ", rpt)
            with open(rpt, "r") as fp:
                for line1 in fp:
                    net  = line1.rstrip()
                    drvNetList.append(net)
            print("drvnet2 count", len(drvNetList))
    bufCell = "HDBLVT08_BUF_4"
    preFix = "yaguo_1027_drvFix"
    drvNetList = list(set(drvNetList))
    #netJsonFile = "./json/smu_zcn1_tu.net.json"
    #netHash =
    #for net in drvNetList:
    #   #fpw.write("catch { add_buffer_on_route "+ net + " -lib_cell " + bufCell +  " -net_prefix " + preFix + " -cell_prefix " + preFix + " -first_distance 10 " + " -repeater_distance 40 -no_legalize -punch_port -verbose}\n")
    #   fpw.write(
    #            "catch { add_buffer_on_route " + net + " -lib_cell " + bufCell + " -net_prefix " + preFix + " -cell_prefix " + preFix + " -repeater_distance 40 -no_legalize -punch_port -verbose}\n")
    #fpw.close()
    print("drvnet count", len(drvNetList))
    return drvNetList
def fixStpByRmBuf(rundir):
    #rpt = rundir + "rpts/SortStpEcoRouteFuncTT0p65vtt0p65v0cEcoRouteGrp/S.INTERNAL.sorted.gz"
    rpt = rundir + "rpts/zcnclk.rpt"
    eco = rundir + "data/stpfix.eco"
    fp = fi.FileInput(rpt, openhook=fi.hook_compressed)
    instList = []
    for line1 in fp:
        if re.search("yaguo_1020_holdFix_\d+\/X\s+\(",line1):
            pin = line1.split()[0]
            if pin.find("vl_wr_smu_zcn1_t1_sms_wrap") < 0 :
                instList.append("/".join(pin.split('/')[0:-1]))

    instList = list(set(instList))
    with open(eco, "w") as fpw:
       for inst in instList:
          fpw.write("catch { remove_buffer " + inst + " }\n")
def fixAll():
    # drvNets = fixDrv(rundir)
    drvNets = []
    dtNets = fixDeltaTrans(rundir)

    drvNets.extend(dtNets)
    drvNetList = list(set(drvNets))

    bufCell = "HDBLVT08_BUF_8"
    preFix = "yaguo_1101_siDelay"
    fpw = open(rundir + "data/drvFix.eco", "w")
    for net in drvNetList:
        fpw.write(
            " add_buffer_on_route " + net + " -lib_cell " + bufCell + " -net_prefix " + preFix + " -cell_prefix " + preFix + " -first_distance 5" + " -repeater_distance_length_ratio 0.5 -no_legalize -punch_port -verbose \n")
    fpw.close()
    # fixStpByRmBuf(rundir)
    fixSiHold()

    # refJsonFile = "json/a.json"
    # tarJsonFile = "json/b.json"
    # ecoFile = "./ecos/place.def"
    ##json2def("./json/diff.json",ecoFile)
    # compareDef(refJsonFile,tarJsonFile,ecoFile)

    # rundir = "/proj/ariel_pd_vol88/yaguo/NLD/0912_eco/main/pd/tiles/ECO_1002_run2/"
    # dsgJsonFile = "./comp.json"
    # libJsonFile = "./lib.json"
    # ctransJsonFile = "./clkTrans.json"
    #
    # ecoFile = "./fixCtrans.tcl"
def compare_json_data(source_data_a,source_data_b):

	def compare(data_a,data_b):
		# type: list
		if (type(data_a) is list):
			# is [data_b] a list and of same length as [data_a]?
			if (
				(type(data_b) != list) or
				(len(data_a) != len(data_b))
			):
				return False

			# iterate over list items
			for list_index,list_item in enumerate(data_a):
				# compare [data_a] list item against [data_b] at index
				if (not compare(list_item,data_b[list_index])):
					return False

			# list identical
			return True

		# type: dictionary
		if (type(data_a) is dict):
			# is [data_b] a dictionary?
			if (type(data_b) != dict):
				return False

			# iterate over dictionary keys
			for dict_key,dict_value in data_a.items():
				# key exists in [data_b] dictionary, and same value?
				if (
					(dict_key not in data_b) or
					(not compare(dict_value,data_b[dict_key]))
				):
					return False

			# dictionary identical
			return True

		# simple value - compare both value and type for equality
		return (
			(data_a == data_b) and
			(type(data_a) is type(data_b))
		)

	# compare a to b, then b to a
	return (
		compare(source_data_a,source_data_b) and
		compare(source_data_b,source_data_a)
	)

class get_cell():
    # if topHash is empty, get the data romve the remote side
    def __init__(self, topHash, instName):
        #print(type(topHash))
        self.fullName = instName
        server = topHash["HOST"]
        py = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        py.connect(server)
        cmd = "INST:"+instName
        py.sendall(cmd.encode())
        data = receiveAll(py)
        topHash["INST"] = {}
        topHash["INST"][instName] = data
        #print(type(data), data)
        py.close()
        '''
        try:
            self.refName = topHash["INST"][instName]["refName"]
        except ValueError:
            print(instName + " was not found")
        try:
            self.llx = topHash["INST"][instName]["llx"]
        except ValueError:
            print(instName + " was not found")
        try:
            self.lly = topHash["INST"][instName]["lly"]
        except ValueError:
            print(instName + " was not found")
        try:
            self.oritation = topHash["INST"][instName]["oritation"]
        except ValueError:
            print(instName + " was not found")

        try:
            self.status = topHash["INST"][instName]["status"]
        except ValueError:
            print(instName + " was not found")
        '''

'''
regression lef2json, lib2josn, libBom2Json
libBom2Json("/proj/ariel_pd_lib1/TSMC7N/library/lib_PD.D.8.1/bom.json","/proj/arielc0pd_fct03/yaguo/json/ariel/fct/")
'''



