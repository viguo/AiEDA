import os, sys,glob,re,stat
import pyLib

memList = ["128x64","256x64","512x64","1024x64","128x128","256x128","512x128","1024x128","128x256","256x256"]
memList = ["128x256", \
           "128x64", \
           "512x64", \
           "256x128", \
           "128x128", \
           "1026x64", \
           "256x32",\
           "256x64", \
           "32x128",\
           "64x128", \
           "64x64", \
           "32x144" \
           "32x128" \
            ]
compilerName = {}
#compilerName["1prf"] = "tsn28hpcp1prf_20120200_130a"
compilerName["2prf"]  = "tsn28hpcp2prf_20120200_130a"
#compilerName["spsram"] = "tsn28hpcpd127spsram_20120200_130a"
#compilerName["uhdspsram"] = "tsn28hpcpuhdspsram_20120200_170a"
#compilerName["dpsram"] = "tsn28hpcpdpsram_20120200_130a"
#compilerName["uhddpsram"] = "tsn28hpcpuhddpsram_20120200_170a"
#compilerName["l1cache"] = "temn28hpcphssrammacros_170a"
#compilerName["l2cache"] = "tsn28hpcpl2spsrammacros_180a"

tsmcCycTime = re.compile('(Cycle time|Minimum cycle time)\s+tcyc\s+(\d+\.\d+)')
tsmcRdTime  = re.compile('(CLK to Valid Q|Access time)\s+tcd\s+(\d+\.\d+)')
tsmcWrTime  = re.compile('(Chip enable setup|Read enable setup)\s+(tcs|trs)\s+(\d+\.\d+)')

tsmcRdCycTime = re.compile('Minimum read cycle time\s+trcyc\s+(\d+\.\d+)')
tsmcWrCycTime = re.compile('Minimum write cycle time\s+twcyc\s+(\d+\.\d+)')
tsmcRdPwr = re.compile('Read\s+(\d+\.\d+)')
tsmcWrPwr = re.compile('Write\s+(\d+\.\d+)')
tsmcLkPwr = re.compile('Leakage Current\s+(\d+\.\d+)')
tsmcDepth = re.compile('(NWORD|NW)\s+\=\s+(\d+)')
tsmcWidth = re.compile('(NBIT|NB)\s+\=\s+(\d+)')
tsmcBweb = re.compile('(BWEB_Enable|Bit_Write)\s+=\s*\"(\w+)\"')
tsmcBist = re.compile('BIST_Enable\s+=\s*\"(\w+)\"')
tsmcSlp = re.compile('SLP_Enable\s+=\s*\"(\w+)\"')
tsmcSd  = re.compile('SD_Enable\s+=\s*\"(\w+)\"')
tsmcMemName = re.compile('CgS__Memory_Name\s+=\s*\"(\S+)"')
tsmcArea = re.compile('\|\s+(\d+\.\d+)\s+\|\s+(\d+\.\d+)\s*\|\s+(\d+\.\d+)\s+\|')
tsmcSeg = re.compile('Segmentation\s+=\s+\"?(\w+)\"?')
tsmcVt  = re.compile('(LVT|Periphery_Vt)\s*=\s*\"(\S+)\"')
tsmcDualRail = re.compile('Dual_Rail_Enable\s+\=\s*\"(\w+)\"')
tsmcMux = re.compile('(NMUX|CM)\s+=\s*(\S+)')
tsmcCompiler = re.compile("Compiler_Name\s+=\s*(\S+)")

memHash = {}
printSeq = ["compiler","name","port","depth", "width","bist","sd","slp","bweb","mux","seg","vt","dualRail","area","leakage","rdPwr","wrPwr","rdCycTime","wrCycTime","rdTime","wrTime"]

dir = "/home/yaguo/works/mc/tsmc/"
for k, v in compilerName.items():
    mc = v
    mcpl = "_".join(mc.split("_")[0:3:2])
    #print(mcpl)
    compDir = dir + mc + "/AN61001_20180125/TSMCHOME/sram/Compiler/"+mc+"/"
    compiler = dir + mc + "/AN61001_20180125/TSMCHOME/sram/Compiler/"+mc+"/"+mcpl +".pl"
    config = dir + mc + "/AN61001_20180125/TSMCHOME/sram/Compiler/"+mc+"/config.txt"

    os.chdir(compDir)
    for file in glob.glob("*.cfg"):
       os.remove(file)
    with open(config,'w') as fconfg:
        for mem in memList:
            for col in ["m2","m4","m8","m16"]:
                for speed in ["s", "f","m"]:
                    fconfg.write(mem + col + speed+"\n")

    #print(os.getcwd())
    #os.system(compiler )
    #os.system(compiler + " -SVT ")
    #os.system(compiler + " -LVT ")
    #os.system(compiler + " -LVT -NonBIST ")
    #os.system(compiler + " -LVT -NonBIST -NonSD")
    #os.system(compiler + " -LVT -NonBIST -NonSD -NonSLP")
    os.environ["MC_HOME"] = os.getcwd()
    if compiler.find("dpsram") > -1:
        os.system(compiler + " -NonBIST  ")
    else:
        os.system(compiler + " -LVT -NonBIST   ")
        os.system(compiler + " -SVT -NonBIST  ")


    for cfgFile in glob.glob("t*.cfg"):
        #print("config file : ",cfgFile)
        with open(cfgFile,"r") as fconfg:
            name = ""
            compiler = ""
            for line in fconfg:
                results = tsmcCompiler.findall(line)
                if len(results) > 0 :
                    compiler = results[0]
                    #memHash[compiler] = {}
                    #print("find config", line, results, len(results))
                results = tsmcMemName.findall(line)
                if len(results) > 0 :
                    name = results[0]
                    try :
                        memHash[compiler][name] = {}
                    except KeyError:
                        memHash[compiler] = {}
                        memHash[compiler][name] = {}
                    memHash[compiler][name]["vt"] = "NA"
                    memHash[compiler][name]["dualRail"] = "NA"
                    #print(compiler, name)
                    if k.find("1p") > -1 or k.find("sp") > -1 :
                        memHash[compiler][name]["port"] = str(1)
                    else:
                        memHash[compiler][name]["port"] = str(2)

                results = tsmcMux.findall(line)
                if len(results) > 0 :
                    memHash[compiler][name]["mux"] = results[0][1]

                results = tsmcDualRail.findall(line)
                if len(results) > 0 :
                    memHash[compiler][name]["dualRail"] = results[0]

                results = tsmcSeg.findall(line)
                if len(results) > 0:
                    memHash[compiler][name]["seg"] = results[0]

                results = tsmcVt.findall(line)
                if len(results) > 0:
                    memHash[compiler][name]["vt"] = results[0][1]
                    #print("VT: " ,results)

                results = tsmcDepth.findall(line)
                if len(results) > 0 :
                    memHash[compiler][name]["depth"] = results[0][1]
                    #print("depth", results[0])

                results = tsmcWidth.findall(line)
                if len(results) > 0:
                    memHash[compiler][name]["width"] = results[0][1]

                results = tsmcBweb.findall(line)
                if len(results) > 0:
                    memHash[compiler][name]["bweb"] = results[0][1]

                results = tsmcSlp.findall(line)
                if len(results) > 0:
                    memHash[compiler][name]["slp"] = results[0]

                results = tsmcSd.findall(line)
                if len(results) > 0:
                    memHash[compiler][name]["sd"] = results[0]

                results = tsmcBist.findall(line)
                if len(results) > 0:
                    memHash[compiler][name]["bist"] = results[0]

                if line.find("CfS__Output_Directory") > -1:
                    outDir = line.split('"')[1]
                    if os.path.isdir(outDir):
                        ssgDS = outDir+"/DATASHEET/"+outDir+"_ssg0p81v125c.ds"
                        ttDS = outDir + "/DATASHEET/" + outDir + "_tt0p9v85c.ds"

                        with open(ssgDS, 'r') as ds:
                            for line in ds:
                                results = tsmcArea.findall(line)
                                if len(results) > 0:
                                    #print(type(area[0]), area[0][0])
                                    memHash[compiler][name]["area"] = results[0][2]
                                    #print("find area", results,name)
                                results = tsmcCycTime.findall(line)
                                if len(results) > 0:
                                    memHash[compiler][name]["rdCycTime"] = results[0][1]
                                    memHash[compiler][name]["wrCycTime"] = results[0][1]

                                results = tsmcRdTime.findall(line)
                                if len(results) > 0:
                                    memHash[compiler][name]["rdTime"] = results[0][1]

                                results = tsmcWrTime.findall(line)
                                if len(results) > 0:
                                    memHash[compiler][name]["wrTime"] = results[0][2]

                                results = tsmcRdCycTime.findall(line)
                                if len(results) > 0:
                                    memHash[compiler][name]["rdCycTime"] = results[0]

                                results = tsmcWrCycTime.findall(line)
                                if len(results) > 0:
                                    memHash[compiler][name]["wrCycTime"] = results[0]

                        with open(ttDS, 'r') as ds:
                            for line in ds:
                                results = tsmcLkPwr.findall(line)
                                if len(results) > 0:
                                    memHash[compiler][name]["leakage"] = results[0]
                                results = tsmcRdPwr.findall(line)
                                if len(results) > 0:
                                    memHash[compiler][name]["rdPwr"] = results[0]
                                results = tsmcWrPwr.findall(line)
                                if len(results) > 0:
                                    memHash[compiler][name]["wrPwr"] = results[0]
                        pyLib.saveJson(memHash, "/home/yaguo/temp/"+name+".json")
                    else:
                        #print(name , outDir, "is not generated,pop")
                        memHash[compiler].pop(name)

pyLib.saveJson(memHash,"/home/yaguo/temp/memHash.json")

tsmcMemSum = "/home/yaguo/temp/tsmcMem.csv"
with open(tsmcMemSum,"w") as fin:
    for i in range(0, len(printSeq)):
        #print(printSeq[i], end=",")
        fin.write(printSeq[i])
        fin.write(",")
    #print()
    fin.write("\n")

    for compiler in sorted(memHash.keys()):

        for mem in sorted(memHash[compiler].keys()):
            #print(mem,end=",")
            fin.write(compiler)
            fin.write(",")
            fin.write(mem)
            fin.write(",")
            for i in range(2,len(printSeq)):
                #print(memHash[compiler][mem][printSeq[i]])

                fin.write(memHash[compiler][mem][printSeq[i]])
                fin.write(",")
            #print("")
            fin.write("\n")
