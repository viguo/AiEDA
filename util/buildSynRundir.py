import os, sys,glob,re,stat
sys.path.insert(0,'/home/yaguo/PycharmProjects/AiEDA/')
import pyLib

configFile = "/home/yaguo/works/pnr/2.syn/config.tcl"
paramHash = {}
with open(configFile,"r") as fin:
    for line in fin:
        line = line.rstrip()
        if len(line) > 1 and line.find("#"):
            #print(line)
            key = line.split("=")[0].replace(" ","")
            val = line.split('\"')[1]
            paramHash[key] = val

pyLib.saveJson(paramHash,"./config.json")
