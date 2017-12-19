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
import glob
import eda2json

eda2json.def2hash()

def loadJson(filePath):
    # open JSON file and parse contents
    print "Lading json",filePath
    start_time = time.time()
    fh = open(filePath,'r')
    data = json.load(fh)
    fh.close()
    print "\t Loading Time :", time.time() - start_time, "S"
    return data

def saveJson(Json,fileName):
    with open(fileName, 'w') as fp:
       json.dump(Json, fp, indent=1)


def clkTranRpt2json ():

    for clkTran in glob.glob(rundir + "rpts/PtDrv*/clock_trans.rpt.gz"):
        print "Reading clock tran report", clkTran
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
            print driver,driverInst, driverRef, driverSlew, value ,limit, driveStrength
            if driverSlew / limit > 0.8:
                print "insert_buffer_on_route -net [get_nets -of [get_pins", driverRef, "/CLK]]"
            elif driveStrength < 6:
                print "size_cell ",driverInst,"HDBLVT08_BUF_CK_8"
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


'''
COMPONENTS 5932511 ;
 - SPARE_lo_2_44 HDBLVT08_FSDPQ_CBV2Y2_1 + FIXED ( 796860 596160 ) FN ;
 - SPARE_lo_2_43 HDBLVT08_FSDPQ_V2Y2_1 + FIXED ( 112974 596160 ) FN ;
 - SPARE_lo_2_42 HDBLVT08_FSDPQ_CBV2Y2_1 + FIXED ( -360696 705600 ) FN ;
'''

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
                print "not suport add cell"
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
                print "not suport add cell"
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
            print "open ", rpt
            with open(rpt,"r") as fp :
                for line1 in fp:
                    net = line1.split()[0]
                    drvNetList.append(net)
            print "drvnet1 count", len(drvNetList)
        elif re.search(r"data_trans",rpt):
            print "open ", rpt
            i2Eco = open(rundir + "/data/dtran.i2.eco", "w")
            with open(rpt, "r") as fp:
                for line1 in fp:
                    #print line1.split()
                    net,driver,refName = line1.split()[0:3]
                    drvNetList.append(net)
                    bufCell = "HDBLVT08_BUF_8"
                    preFix = "yaguo_1101_dtranFix"
                    #i2Eco.write(" buffer_pin " + driver + " " + bufCell + " " + preFix + " \n")
            print "drvnet1 count", len(drvNetList)

        elif re.search(r'si_bottleneck|glitch',rpt):
            print "open ", rpt
            with open(rpt, "r") as fp:
                for line1 in fp:
                    net  = line1.rstrip()
                    drvNetList.append(net)
            print "drvnet2 count", len(drvNetList)
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
    print "drvnet count", len(drvNetList)
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


if __name__=='__main__':
    #defFileName = 'C:/parser_case/COMPS.def.gz'
    #defFileName = 'C:/parser_case/Place.def.gz'
    rundir = "/proj/ariel_pd_vol88/yaguo/NLD/1030_eco/main/pd/tiles/ECO_1030_run4/"
    #drvNets = fixDrv(rundir)
    drvNets  = []
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
    #fixStpByRmBuf(rundir)
    fixSiHold()

    #refJsonFile = "json/a.json"
    #tarJsonFile = "json/b.json"
    #ecoFile = "./ecos/place.def"
    ##json2def("./json/diff.json",ecoFile)
    #compareDef(refJsonFile,tarJsonFile,ecoFile)

    #rundir = "/proj/ariel_pd_vol88/yaguo/NLD/0912_eco/main/pd/tiles/ECO_1002_run2/"
    #dsgJsonFile = "./comp.json"
    #libJsonFile = "./lib.json"
    #ctransJsonFile = "./clkTrans.json"
    #
    #ecoFile = "./fixCtrans.tcl"


'''
    clkTranRpt2json()
    with open(dsgJsonFile, 'r') as fp:
        print "Loading Json ", dsgJsonFile
        dsgHash = json.load(fp)


    with open(libJsonFile, 'r') as fp:
        print "Loading Json ", libJsonFile
        libHash = json.load(fp)
        fp.close()

    with open(ctransJsonFile, 'r') as fp:
        print "Loading Json ", ctransJsonFile
        rptHash = json.load(fp)
        fp.close()
    fixCTrans(dsgHash, libHash, rptHash,ecoFile)

'''

