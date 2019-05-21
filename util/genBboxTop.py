import os, time, random
import sys
import sys
sys.path.insert(0,'../')
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

topName = "blk_otn_ts_schd"
subModuleNumb = 16
connectWireNumb = 15
inputWireNumb = (connectWireNumb + 1) * subModuleNumb  -1
outputWireNumb = (connectWireNumb + 1) * subModuleNumb  -1

invCell = "INVRTND1BWP7D5T16P96CPD"

bboxModuleSample = '''
module bboxModulePostfix (
 moduleSI ,
 moduleSO  
);
input inputWidth moduleSI;
output outputWidth moduleSO;

AutoInstance
endmodule
'''


with open("./bboxTop.v", "w") as fp:
    subModuleInst = ""
    for i in range(0,inputWireNumb+1):
        bufName = " inst_" + str(i)
        subModuleInst += invCell + bufName + " (.I(moduleSI[" + str(i) + "]), .ZN(moduleSO[" + str(i) + "]));\n"
    for i in range(0,subModuleNumb):

        subModule = bboxModuleSample
        subModule = subModule.replace("Postfix",str(i))
        subModule = subModule.replace("inputWidth",  "[" + str(inputWireNumb)  + ":0]")
        subModule = subModule.replace("outputWidth", "[" + str(outputWireNumb) + ":0]")
        subModule = subModule.replace("AutoInstance",subModuleInst)
        fp.write(subModule)

    topModule = bboxModuleSample
    topModule = topModule.replace("bboxModulePostfix", topName)
    topModule = topModule.replace("moduleSI", "topSI")
    topModule = topModule.replace("moduleSO", "topSO")
    topModule = topModule.replace("inputWidth", "[0:" + str(inputWireNumb) + "]")
    topModule = topModule.replace("outputWidth", "[0:" + str(outputWireNumb) + "]")
    moduleConnect = {}
    moduleConnectAll = ""
    wire = ""

    for i in range(0, subModuleNumb):
        if i == 0:
            wire = "wire [0:" + str(inputWireNumb) + "] topSI;\n"
            wire += "wire " + "[0:" + str(inputWireNumb) + "] net_" + str(i) + ";\n"
        elif i == subModuleNumb - 1:
            wire = "wire [0:" + str(inputWireNumb) + "] topSO;\n"
        else:
            wire = "wire "  + "[0:" + str(inputWireNumb) + "]  net_" + str(i)+ ";\n"

        moduleConnectAll += wire
    #print("DBEUG")

    for i in range(0,subModuleNumb):
        j = str(i - 1)
        if i == 0:
            i = str(i)
            moduleConnect[i] = "bboxModule"+i + "  inst_"+ i + " (\n"
            moduleConnect[i] += ".moduleSI(" + "topSI), \n"
            moduleConnect[i] += ".moduleSO(net_" + i  + "));\n\n"
        elif i == subModuleNumb -1:
            i = str(i)
            moduleConnect[i] = "bboxModule"+i + "  inst_"+ i + " (\n"
            moduleConnect[i] += ".moduleSI(net_" + j  + "),\n"
            moduleConnect[i] += ".moduleSO(" + "topSO ));\n\n"

        else:
            i = str(i)
            moduleConnect[i] = "bboxModule" + i + "  inst_"+ i + " (\n"
            moduleConnect[i] += ".moduleSI(net_" + j + "),\n"
            moduleConnect[i] += ".moduleSO(net_" + i + "));\n\n"
        moduleConnectAll += moduleConnect[i]
    #print(moduleConnectAll)
    topModule = topModule.replace("AutoInstance",moduleConnectAll)
    fp.write(topModule)
##connect top


