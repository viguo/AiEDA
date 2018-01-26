'''
comapre the memory  util
'''
import os, sys,glob,re

snpsMem = "/Users/guoyapeng/Downloads/snps/*.ds"
sumResult = "/Users/guoyapeng/Downloads/memCompare.txt"
memAttr = {}

snpsPort = re.compile('(Two|Single)\s+Port')
snpsName  = re.compile('Memory Name\s+\:\s+(\w+)')
snpsSize  = re.compile('Memory Size\s+\:\s+(\d+)\s+words\s+x\s+(\d+)')
snpsColumn = re.compile('Column Mux Option\s+\:\s+')
snpsArea = re.compile('Memory Area\s+\:\s+(\S+)\s+x\s+(\S+)\s+=\s+(\S+)\s+')
snpsBitCel = re.compile('Bitcell Area\s+\:\s+(\S+)\s+')
snpsRdPwr  = re.compile('Power Dissipation\s+\|(\S+)\|')
snpsOpFreq = re.compile('Operating Frequency range\s+\:\s+(\d+)')

for mem in glob.glob(snpsMem):
    with open(mem,"rt") as fin:
        name = ""
        for line in fin:
            portType = snpsPort.findall(line)
            if len(portType) > 0:
                if portType[0] == "Two":
                    port = 2
                else:
                    port = 1
                #print(port)
            ramName = snpsName.findall(line)
            if len(ramName) > 0:
                name = ramName[0]
                memAttr[name] = {}
                memAttr[name]["port"] = port

            ramSize = snpsSize.findall(line)
            if len(ramSize) > 0:
                memAttr[name]["depth"] = list(ramSize[0])[0]
                memAttr[name]["width"] = list(ramSize[0])[1]
            ramArea = snpsArea.findall(line)
            if len(ramArea) > 0 :
                memAttr[name]["area"] = list(ramArea[0])[2]
                #print(ramArea)
            ramBit = snpsBitCel.findall(line)
            if len(ramBit) > 0:
                #print(ramBit)
                memAttr[name]["bitCell"] = ramBit[0]
            rdPwr = snpsRdPwr.findall(line)
            if len(rdPwr) > 0:
                memAttr[name]["rdPwrPerMHz"] = float(rdPwr[0].split("|")[0]) * float(memAttr[name]["width"])
                #print(name, rdPwr[0].split("|"))
            ramFreq = snpsOpFreq.findall(line)
            if len(ramFreq) > 0:
                memAttr[name]["minFreq"] = ramFreq[0]

outputFormat = ["name", "port", "depth", "width", "area", "bitCell", "rdPwrPerMHz", "minFreq"]

with open(sumResult, "wt") as fout:
    fout.write(" ".join(outputFormat))
    fout.write("\n")
    print(*outputFormat)
    for memName in memAttr:
        print(memName," ", end="")
        fout.write(memName)
        for i in range(1,len(outputFormat)):
            key = outputFormat[i]
            #print(key,i,memAttr[memName][key],end="#")
            print(memAttr[memName][key],end="")
            print("  ", end="")
            fout.write(str(memAttr[memName][key]))
            fout.write(" ")
        print("")
        fout.write("\n")













