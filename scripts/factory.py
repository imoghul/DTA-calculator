import csv,json
import glob
import os
import sys
from utils import *
import random
import string
from certificate import *
import threading

outFileName = "summary.csv"
globType = "**/*.csv"

preferencesFile = None



detectionList_FT2_SUM = None
detectionList_FT3 = None
retrieveData = None
regions = []
data = {}
headers = []
currentSN = None
certdir = None
genCert = False

def calc(fileName):
    global currentSN,data
    fileType = None
    if("_SUM" in fileName): 
        with open(fileName, newline='') as file:
            sn =""
            region = ""
            for row in csv.reader(file, delimiter='\n', quotechar=','):
                for r in row:
                    v = r.split(',')
                    if("SN" in v or "Serial Number" in v):
                        sn = v[1]
                        currentSN = sn
                        if(sn not in data.keys()):
                            data[sn] = {}
                            data[sn]["Serial Number"] = sn
                            continue
                    if(len(v)==1):
                        region = v[0]
                        # data[sn][region] = {}
                        if(region not in regions): regions.append(region)
                    for i in detectionList_FT2_SUM:
                        index = i["column"]-1#int(i.split("@")[-1])-1
                        dataField = i["title"]#i.split("@")[0]
                        dataRegion = None if "region" not in i else i["region"]
                        if dataRegion==None and dataField==v[0]:
                            # print(fileName,dataField)
                            data[sn][dataField] = v[index]
                        if dataRegion!=None and (dataField in v and region == dataRegion):
                            data[sn][region+":"+dataField] = v[index] if v[index]!="" else "0"#"not calibrated"
            _date = fileName.split("_")[-3]
            data[sn]["Date"] =  _date[4:6]+"/"+_date[6:8]+"/"+_date[0:4]
            data[sn]["File Name:FT2 SUM"] = fileName.split("\\")[-1]
    elif("_RAW" in fileName): 
        fileType = "FT2 RAW"
        return False
    elif("FT3_" in fileName or "ft3_" in fileName): 
        with open(fileName, newline='') as file:
            ft3headers = None
            sn = None
            for row in csv.reader(file, delimiter='\n', quotechar=','):
                for r in row:
                    v = r.split(',')
                    if(ft3headers == None): ft3headers = v
                    else:
                        # print(ft3headers)
                        sn = v[ft3headers.index("Serial Number")] 
                        if(sn not in data):
                            data[sn] = {}
                            data[sn]["Serial Number"] = sn
                        for i in detectionList_FT3:
                            if(i in ft3headers):
                                try:
                                    data[sn][i] = v[ft3headers.index(i)]
                                except:
                                    pass
                        data[sn]["File Name:FT3"] = fileName.split("\\")[-1]
    else:
        fileType = "FT1"
        return False
    return True


def writeHeaderToFile(writer):
    global headers
    headers = [(h["title"] if "region" not in h else h["region"]+":"+h["title"]) for h in detectionList_FT2_SUM] + [h for h in detectionList_FT3]
    headers.insert(0,"File Name:FT3")
    headers.insert(0,"File Name:FT2 SUM")
    headers.insert(0,"Date")
    headers.insert(0,"Serial Number")
    writer.writerow(headers)


def writeDataToFile(writer, dir, fileNames):
    counter = 0
    length = len(fileNames)
    global certdir
    for fileName in fileNames:
        # try:
            success = calc(fileName)
            counter+=1
            if(counter>length):return
            process_bar("Retrieving",counter,length,message="Reading from "+dir)
        # except:
        #     print(fileName + " couldn't be read")
    # print(data)
def writeSummaryToFile(writer):
    counter = 0
    length = len(data)
    for sn in data:
        counter+=1
        writer.writerow([data[sn][h] if h in data[sn] else "doesn't exist" for h in headers])
        if(genCert and "Date" in data[sn] and "TestResult" in data[sn]):
            createCertificate(sn,data[sn]["Date"],"Pass" if data[sn]["TestResult"]=="Test Complete" else "Fail",certdir)
        process_bar("Writing Data",counter,length)

def transferDirs(cdir,pdir):
    global certdir,preferencesFile,detectionList_FT2_SUM,detectionList_FT3,retrieveData,genCert
    certdir = cdir
    preferencesFile = pdir
    with open(preferencesFile) as f:
        retrieveData = json.load(f)
    detectionList_FT2_SUM = retrieveData["Test Preferences"]["FT2 SUM"] if "FT2 SUM" in retrieveData["Test Preferences"] else []
    detectionList_FT3 = retrieveData["Test Preferences"]["FT3"] if "FT3" in retrieveData["Test Preferences"] else []
    genCert = retrieveData["Generate Certificates"]
