import os, time, random
import sys
import sys
sys.path.insert(0,'../')
#import pandas as pd
import csv
ft = open("topFT.invs.const","w")

###topFT.conf format is
# netName parA parB
#df = pd.read_csv('./topFT.csv',index_col='busName')
#print(df)
#print(df.head())
#print(df.info())

with open('./topFT.csv', newline='') as csvfile:
    #spamreader = csv.reader(csvfile)
    ft.write("version 1.0;")
    spamreader = csv.DictReader(csvfile)
    for row in spamreader:
        #print(row["lowBit"])
        busName = row["busName"]
        if row["midParList"] != "Null":
            for i in range(int(row["lowBit"]),int(row["highBit"])+1):
                netName = busName + "[" + str(i) + "]"
                netFT = "\nnet "+  netName
                if row["startPar"] == "input":
                    netFT += "io-hinst "
                    #netFT += netName + " " + row[""]
                else:
                    midList = row["midParList"].split()
                    for i in range(0,len(midList)+1):
                        if i == 0:
                            #print(row["startPar"], midList[i])
                            ftPath = row["startPar"] + " " + midList[i]
                        elif i == len(midList):
                            ftPath = midList[i-1] + " " + row["endPar"]
                        else:
                            #print(midList[i-1],midList[i])
                            ftPath = midList[i-1] + " " + midList[i]
                        netFT += "\nhinst-hinst " +  ftPath + ";"
                    netFT += "\nend net"
                ft.write(netFT)
        else:
            print("skip net",busName)

ft.close()
        #print(type(row))
        #if row[0] != ("busName") :
