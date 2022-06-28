import csv
from datetime import datetime
import json
import glob
import os
import sys
from utils import *
import random
import string
from certificate import *
import threading
import dateutil.parser

outFileName = "summary.csv"
globType = "**/*.csv"

preferencesFile = None


dirNum = 0

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
    global currentSN, data, headers
    fileType = getFileType(fileName)
    if(fileType == "FT2 SUM"):
        with open(fileName, newline='') as file:
            sn = ""
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
                    if(len(v) == 1):
                        region = v[0]
                        if(region not in regions):
                            regions.append(region)
                    for i in detectionList_FT2_SUM:
                        index = i["column"]-1 
                        dataField = i["title"]
                        dataKey = getFT2SUMTitle(i)
                        dataRegion = None if "region" not in i else i["region"]
                        if(type(dataField)!=list):
                            if dataRegion == None and dataField == v[0]:
                                data[sn][dataKey] = v[index]
                            if dataRegion != None and (dataField in v and region == dataRegion):
                                data[sn][dataKey] = v[index] if v[index] != "" else "0"
                        elif type(dataField)==list:
                            
                            if dataRegion == None and all([i in v for i in dataField]):
                                data[sn][dataKey] = v[index]
                            if dataRegion != None and (all([i in v for i in dataField]) and region == dataRegion):
                                data[sn][dataKey] = v[index] if v[index] != "" else "0"
                                # print(sn,data[sn][dataKey])
            _date = fileName.split("_")[-3]
            data[sn]["Date"] = _date[4:6]+"/"+_date[6:8]+"/"+_date[0:4]
            data[sn]["File Name:FT2 SUM"] = fileName.split("\\")[-1]
    elif(fileType == "FT2 RAW"):
        return False
    elif(fileType == "FT3"):
        with open(fileName, newline='') as file:
            ft3headers = None
            sn = None
            for row in csv.reader(file, delimiter='\n', quotechar=','):
                for r in row:
                    v = r.split(',')
                    if(ft3headers == None):
                        ft3headers = v
                    else:
                        sn = v[ft3headers.index("Serial Number")]
                        _date = v[ft3headers.index("TimeStamp")].split(" ")[0]
                        if(sn not in data):
                            data[sn] = {}
                            data[sn]["Serial Number"] = sn
                            data[sn]["Date"] = _date
                            data[sn]["Model ID"] = v[ft3headers.index("Model ID")]
                        for i in detectionList_FT3:
                            if(i in ft3headers):
                                try:
                                    data[sn][i] = v[ft3headers.index(i)]
                                except:
                                    pass
                        data[sn]["File Name:FT3"] = fileName.split("\\")[-1]
    elif(fileType == "FT1"):
        return False
    return True


def writeHeaderToFile(writer):
    pass
    # global headers
    # headers = [(h["title"] if "region" not in h else h["region"]+":"+h["title"]+(":"+h["column header"] if "column header" in h else ""))
    #            for h in detectionList_FT2_SUM] + [h for h in detectionList_FT3]
    # headers.insert(0, "File Name:FT3")
    # headers.insert(0, "File Name:FT2 SUM")
    # headers.insert(0, "Date")
    # headers.insert(0, "Serial Number")
    # print(headers)
    # writer.writerow(headers)


def writeDataToFile(writer, dir, fileNames):
    global dirNum
    dirNum += 1
    counter = 0
    length = len(fileNames)
    global certdir
    for fileName in fileNames:
        try:
            success = calc(fileName)
            counter += 1
            if(counter > length):
                return
            process_bar("Retrieving", counter, length,
                        message="Reading from the %s directory" % ordinal(dirNum))
        except:
            print(fileName + " couldn't be read")
    
    
    


def writeSummaryToFile(writer):
    global data
    # sort data
    # try:
    data = {k: v for k, v in sorted(data.items(), key=lambda sn: datetime.strptime(str(dateutil.parser.parse(sn[1]["Date"])).split(" ")[0],"%Y-%m-%d"))}
    # except:pass
    # header calculating
    global headers
    for i in data:
        for j in data[i]:
            if j not in headers: headers.append(j)
    for i in reversed(detectionList_FT3):
        moveToBeginning(headers,i)
    for i in reversed([getFT2SUMTitle(j) for j in detectionList_FT2_SUM]):
        moveToBeginning(headers,i)
    moveToBeginning(headers,"File Name:FT3")
    moveToBeginning(headers,"File Name:FT2 SUM")
    moveToBeginning(headers,"Date")
    moveToBeginning(headers,"Serial Number")
    writer.writerow(headers)

    # writing data
    counter = 0
    length = len(data)
    for sn in data:
        if getSkippable(sn): 
            length-=1
            continue                

        counter += 1

        writer.writerow([data[sn][h] if h in data[sn]
                        else "doesn't exist" for h in headers])
        if(genCert and "Date" in data[sn] and "TestResult" in data[sn]):
            createCertificate(sn, data[sn]["Date"], "Pass" if data[sn]
                              ["TestResult"] == "Test Complete" else "Fail", certdir)
        process_bar("Writing Data", counter, length)


def transferDirs(cdir, pdir):
    global certdir, preferencesFile, detectionList_FT2_SUM, detectionList_FT3, retrieveData, genCert
    certdir = cdir
    preferencesFile = pdir
    with open(preferencesFile) as f:
        retrieveData = json.load(f)
    detectionList_FT2_SUM = retrieveData["Test Preferences"][
        "FT2 SUM"] if "FT2 SUM" in retrieveData["Test Preferences"] else []
    detectionList_FT3 = retrieveData["Test Preferences"]["FT3"] if "FT3" in retrieveData["Test Preferences"] else [
    ]
    genCert = retrieveData["Generate Certificates"]


def getSkippable(sn):
    global data,retrieveData
    skip = False
    if("Avoid" in retrieveData):
        for i in retrieveData["Avoid"]:
            if anyIn(data[sn][i],retrieveData["Avoid"][i]): skip = True
    if("Limit" in retrieveData):
        for i in retrieveData["Limit"]:
            
            try:
                if not anyIn(data[sn][i],retrieveData["Limit"][i]):
                    skip = True
            except:print(data[sn])
    if("Dates" in retrieveData):
        isIn = False
        for i in retrieveData["Dates"]:
            snDate = dateutil.parser.parse(data[sn]["Date"])
            snDate = {
                "Day":snDate.day,
                "Month":snDate.month,
                "Year":snDate.year
            }
            if("Day" not in i):
                del snDate["Day"]
            if("Month" not in i):
                del snDate["Month"]
            if("Year" not in i):
                del snDate["Year"]
            
            if(snDate == i): isIn = True
            # print(i,snDate,isIn)
        if(not isIn): skip = True
    return skip
