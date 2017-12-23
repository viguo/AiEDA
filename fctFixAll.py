import os
#import sys; sys.path.insert(0, os.getenv('/home/yaguo/scripts/amdPython3'))
import eda2json as ej
import json



if __name__=='__main__':

    jsonOut = "/proj/arielc0pd_fct03/yaguo/json/ariel/fct/"
    #jsonOut = "/proj/arielc0pd_fct03/yaguo/json/ariel/irem/"
    #libBomFile = "/proj/ariel_pd_lib1/TSMC7N/library/lib_PD.D.8/bom.json"
    #libBom2Json(libBomFile,jsonOut)

    #topName = "mpu"
    #topHash  = ej.loadJsonGzip(jsonOut+topName+".only.inst.json.gz")
    #tileHash = ej.loadJsonGzip(jsonOut+"tiles.inst.json.gz")
    #ej.saveJsonGzip(ej.flatTopTile(topHash,tileHash),jsonOut+topName+".inst.json.gz")
    #exit()

    topName = "mpu"
    slackTableFile = "/proj/arielc0pd_fct03/yaguo/json/ariel/ilm.pintiming_table.rpt.gz"
    topHash = ej.readSlackTable(slackTableFile)

    fctBomFile = "/proj/ariel_pd_fct3/fct_eco_runs/func_flat_normal/fct113_ECO_Func_Flat_EcoRoute_Dec04/data/bom.json"
    topHash.update(ej.fctBom2Json(fctBomFile,jsonOut,topName)["INST"])
    ej.saveJsonGzip(topHash["NET"], jsonOut + topName + ".net.json.gz")
    ej.saveJsonGzip(topHash["PIN"], jsonOut + topName + ".pin.json.gz")
    ej.saveJsonGzip(topHash["INST"], jsonOut + topName + ".inst.json.gz")

    #newTile.json = tile2top (tile.json, mpu.json)
    #delay = cellDelay (inputTran, ouptuLoad, refname,  fromPin ,toPi



'''
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
