import csv
import glob
import os
import sys
from utils import *
import random
import string
from certificate import *

outFileName = "summary.csv"
globType = "**/*SUM*.csv"

with open("EOLT-Test-Analyzer/preferences.txt") as f:
    detectionList = f.readlines()
detectionList = [i[0:-1] if(i[-1]=="\n") else i for i in detectionList]
print(detectionList)

regions = []
data = {}
headers = [h.split("@")[0] for h in detectionList]
headers.insert(0,"Date")
headers.insert(0,"File Name")
headers.insert(0,"SN")
currentSN = None
certdir = None
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

def calc(fileName):
    global currentSN
    with open(fileName, newline='') as file:
        sn =""
        region = ""
        for row in csv.reader(file, delimiter='\n', quotechar=','):
            for r in row:
                v = r.split(',')
                if("SN" in v or "Serial Number" in v):
                    sn = v[1]
                    currentSN = sn
                    data[sn] = {}
                    data[sn]["SN"] = sn
                    data[sn]["File Name"] = fileName.split("\\")[-1]
                    continue
                if(len(v)==1):
                    region = v[0]
                    # data[sn][region] = {}
                    if(region not in regions): regions.append(region)
                for i in detectionList:
                    index = int(i.split("@")[-1])-1
                    dataField = i.split("@")[0]
                    if dataField==v[0]:
                        data[sn][dataField] = v[index]
                    if ':' in i:
                        temp = i.split(':')
                        tempRegion = temp[0]
                        tempData = temp[1].split("@")[0]#" ".join(temp[1].split("@")[0:-1])
                        if(tempData in v and region == tempRegion):
                            """data[sn][region][tempData]"""
                            data[sn][region+":"+tempData] = v[index] if v[index]!="" else "0"#"not calibrated"
        _date = fileName.split("_")[-3]
        data[sn]["Date"] =  _date[4:6]+"/"+_date[6:8]+"/"+_date[0:4]


def writeHeaderToFile(writer):
    writer.writerow(headers)


def writeDataToFile(writer, dir, fileNames):
    counter = 0
    length = 100#len(fileNames)
    global certdir
    for fileName in fileNames:
        try:
            counter+=1
            if(counter>length):return
            process_bar("Processing",counter,length)
            calc(fileName)
            writer.writerow([data[currentSN][h] if h in data[currentSN] else "doesn't exist" for h in headers])
            # createCertificate(currentSN,data[currentSN]["Date"],"Pass" if data[currentSN]["TestResult"]=="Test Complete" else "Fail",certdir)
        except:
            print(fileName + " couldn't be read")

def writeSummaryToFile(writer):
    pass

def transferCertDir(dir):
    global certdir
    certdir = dir
