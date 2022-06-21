import csv
import glob
import os
import sys
from utils import *
import random
import string

randStr = (''.join(
    random.choice(string.ascii_lowercase + string.digits +
                  string.ascii_uppercase) for i in range(20)))
# + input("Output file Location (TONGRUN/): ")
outFileName = "summary.csv"
globType = "**/*SUM*.csv"
detectionList = ["Model ID@2","Calibration Data:Air1@5","Calibration Data:Air2@5","Calibration Data:Glycol@5","Post Calibration Data:Air1@5","Post Calibration Data:Air2@5","Post Calibration Data:Glycol@5"]

data = {}
# 
#    Dictionary that stores all data as such:
#    {
#       SN: {
#               filename, model id, etc.: ...
#               region name: {
#                               Air1, Air2, Glyclol: ... 
#                            }
#           }
#    }
# 

def fixDupl(arr):
    common = [i for i in arr if arr.count(i) > 1]
    for val in common:
        temp = 1
        for i in range(len(arr)):
            if arr[i] == val:
                arr[i] += randStr + str(temp) + "(%d)" % temp
                temp += 1
    return (arr)


def calc(fileName):
    with open(fileName, newline='') as file:
        sn =""
        region = ""
        for row in csv.reader(file, delimiter='\n', quotechar=','):
            for r in row:
                v = r.split(',')
                if("SN" in v or "Serial Number" in v):
                    sn = v[1]
                    data[sn] = {}
                    data[sn]["SN"] = sn
                    data[sn]["filename"] = fileName.split("\\")[-1]
                    continue
                if(len(v)==1):
                    region = v[0]
                    data[sn][region] = {}
                for i in detectionList:
                    index = int(i.split("@")[-1])-1
                    dataField = i.split("@")[0]
                    if dataField in v:
                        data[sn][dataField] = v[index]
                    if ':' in i:
                        temp = i.split(':')
                        tempRegion = temp[0]
                        tempData = temp[1].split("@")[0]#" ".join(temp[1].split("@")[0:-1])
                        if(tempData in v and region == tempRegion):
                            data[sn][region][tempData] = v[index] if v[index]!="" else "not calibrated"
                
                    





def writeHeaderToFile(writer):
    pass


def writeDataToFile(writer, dir, fileNames):
    counter = 0
    length = len(fileNames)
    for fileName in fileNames:
        try:
            counter+=1
            # if(counter>=100):return
            process_bar(counter,length)# print("%f%"%100*counter/length)
            calc(fileName)
        except:
            print(fileName + " couldn't be read")


def writeSummaryToFile(writer):
    headers = [h.split("@")[0] for h in detectionList]
    headers.insert(0,"filename")
    headers.insert(0,"SN")
    regions = []
    
    for d in data:
        for i in data[d]:
            if(type(data[d][i])==dict and i not in regions): regions.append(i)
                
    dataTemp = data.copy()
    
    # fix nested dicts 
    # this code essentially converts a nested dict for example:
    # {Model ID:..., Calibration:{Air1:...,Air2:...,Glycol:...}}
    # into
    # {Model ID:..., "Calibration:Air1":...,"Calibration:Air2":...,"Calibration:Glycol":...}
    for d in data: 
        for r in regions:
            try:
                vals = data[d][r]
                for v in vals:
                    data[d][r+":"+v] = data[d][r][v]
                del data[d][r]
            except:
                print("bad")
                pass
       
    writer.writerow(headers)
    for d in data:
        outlist = []
        for h in headers:
            outlist.append(data[d][h] if h in data[d] else "doesn't exist")
        writer.writerow(outlist)
