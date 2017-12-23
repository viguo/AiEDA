import os, time, random
import icComVar as icVar
import pyparsing as pp
import re
import json
import multiprocessing as mp
import glob
import sys; sys.path.insert(0, os.getenv('FLOW_dir','/home/yaguo/scripts/eda2json/'))
import eda2json as ej


if __name__=='__main__':

    paramHash = ej.params2Json("./tile.params")
    print("NICKNAME:", paramHash["NICKNAME"])
    rundir = paramHash["BASE_DIR"] +"/data/"
    fctBomFile = rundir + "bom.json"
    topModule = paramHash["TOP_MODULE"]
    ej.fctBom2Json(fctBomFile,rundir,topModule)



