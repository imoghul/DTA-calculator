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
import re
import dateutil.parser

outFileName = "summary.csv"
globType = "**/*.csv"

preferencesFile = None

randStr = (''.join(random.choice(string.ascii_lowercase + string.digits +string.ascii_uppercase) for i in range(20)))
dirNum = 0

detectionList = {
    "FT2 SUM": [],
    "FT3": [],
    "FT2 RAW": [],
    "FT1": []
}
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

    # # # # # # # # # # # # # # # # # # # # # # # #
    # THEORETICALLY WORKING BUT RISIKY CODE BELOW #
    # # # # # # # # # # # # # # # # # # # # # # # #

    if("s p e e d" in retrieveData and retrieveData["s p e e d"] and (fileType == "FT2 SUM" or fileType == "FT2 RAW")):
        isIn = None
        if "Limit" in retrieveData:
            if "Serial Number" in retrieveData["Limit"]:
                if anyIn(fileName, retrieveData["Limit"]["Serial Number"]):
                    isIn = True
                else:
                    isIn = False
            if "Model ID" in retrieveData["Limit"]:
                if anyIn(fileName, retrieveData["Limit"]["Model ID"]):
                    isIn = True
                else:
                    isIn = False
        if isIn == False:
            return

    # # # # # # # # # # # # # # # # # # # # # # # #
    #                                             #
    # # # # # # # # # # # # # # # # # # # # # # # #

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
                    for i in detectionList["FT2 SUM"]:
                        try:
                            index = i["column"]-1
                            dataField = i["title"]
                            dataKey = getTitle_config(i)
                        except:
                            raise Exception(
                                "One or more required keys in an FT2 SUM preference are missing")
                        
                        dataRegion = None if "region" not in i else i["region"]
                        if(type(dataField) != list):
                            if dataRegion == None and dataField == v[0]:
                                data[sn][dataKey] = v[index]
                            if dataRegion != None and (dataField in v and region == dataRegion):
                                data[sn][dataKey] = v[index] if v[index] != "" else "0"
                        elif type(dataField) == list:
                            allIn = all([i in v for i in dataField])
                            if dataRegion == None and allIn:
                                data[sn][dataKey] = v[index]
                            if dataRegion != None and (allIn and region == dataRegion):
                                data[sn][dataKey] = v[index] if v[index] != "" else "0"
            _date = fileName.replace(".csv", "").split("_")
            index = 1
            for i in range(len(_date)):
                if("SUM" in _date[i]):
                    index = i
            _date = _date[index-2]
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
                            data[sn]["Model ID"] = v[ft3headers.index(
                                "Model ID")]
                        for i in detectionList["FT3"]:
                            title = getTitle_config(i)
                            if(title in ft3headers):
                                try:
                                    data[sn][title] = v[ft3headers.index(
                                        title)]
                                except:
                                    pass
                        data[sn]["File Name:FT3"] = fileName.split("\\")[-1]
    elif(fileType == "FT1"):
        return False
    return True


def writeHeaderToFile(writer):
    # check for duplicates
    check = []
    dups = False
    for i in detectionList["FT3"]:
        if i not in check:
            check.append(i)
        else:
            dups = True
    for i in detectionList["FT2 SUM"]:
        title = getTitle_config(i)
        if title not in check:
            check.append(title)
        else:
            dups = True

    if(dups):
        raise Exception(
            "Cannot have duplicates in header. Please check your preferences.json and resolve issue")


def writeDataToFile(writer, dir, fileNames):
    global dirNum
    dirNum += 1
    counter = 0
    length = len(fileNames)
    global certdir
    for fileName in fileNames:
        counter += 1
        process_bar("Retrieving from the %s directory" %
                    ordinal(dirNum), counter, length)
        try:
            success = calc(fileName)

            if(counter > length):
                return

        except Exception as e:
            print(fileName + " couldn't be read with the following error: "+str(e))


def writeSummaryToFile(writer):
    global data
    # sort data
    try:
        data = {k: v for k, v in sorted(data.items(), key=lambda sn: datetime.strptime(
            str(dateutil.parser.parse(sn[1]["Date"])), "%Y-%m-%d %H:%M:%S"))}
    except:
        print("Bad date exists, will not sort by date")
    # header calculating
    global headers
    for i in data:
        for j in data[i]:
            if j not in headers:
                headers.append(j)
    for i in reversed([getTitle_config(j) for j in detectionList["FT3"]]):
        moveToBeginning(headers, i)
    for i in reversed([getTitle_config(j) for j in detectionList["FT2 SUM"]]):
        moveToBeginning(headers, i)
    moveToBeginning(headers, "File Name:FT3")
    moveToBeginning(headers, "File Name:FT2 SUM")
    moveToBeginning(headers, "Date")
    moveToBeginning(headers, "Serial Number")
    for test in detectionList:
        for pref in detectionList[test]:
            if "hide" in pref and pref["hide"]:
                headers.remove(getTitle_config(pref))
    writer.writerow(headers)

    # writing data
    counter = 0
    length = len(data)
    for sn in data:
        counter += 1
        process_bar("Writing Data", counter, length)

        for h in headers:
            if(h not in data[sn]):
                data[sn][h] = "doesn't exist"

        if getSkippable(sn):
            continue

        writer.writerow([data[sn][h] for h in headers])
        try:
            if(genCert and "Date" in data[sn] and "TestResult" in data[sn]):
                createCertificate(sn, data[sn]["Date"], "Pass" if data[sn]
                                  ["TestResult"] == "Test Complete" else "Fail", data[sn][randStr+"CERTIFICATE:DAQ TEMP"] if randStr+"CERTIFICATE:DAQ TEMP" in data[sn] else "N/A", data[sn][randStr+"CERTIFICATE:CALIB"] if randStr+"CERTIFICATE:CALIB" in data[sn] else "N/A", certdir)
        except:
            raise Exception(
                "Couldn't generate certificate, check config file for correct preferences")
    if("PDF Certificates" in retrieveData and retrieveData["PDF Certificates"] == True and "Generate Certificates" in retrieveData and retrieveData["Generate Certificates"] == True):
        # counter = 0
        # docs = glob.glob(certdir+"*_certificate*.docx")
        # # print(docs)
        # length = len(docs)
        # for i in docs:
        #     counter += 1
        #     # process_bar("Converting to PDF", counter, length)
        #     convertToPDF_doc(i)

        convertToPDF_path(certdir)


def transferDirs(cdir, pdir):
    global certdir, preferencesFile, detectionList, retrieveData, genCert
    certdir = cdir
    preferencesFile = pdir
    try:
        with open(preferencesFile) as f:
            retrieveData = json.load(f)
    except(PermissionError):
        raise Exception(
            "Preferences file couldn't be opened. Close the file if it is open")
    except Exception as e:
        raise e

    try:
        retrieveData["Test Preferences"].append({
            "test": "FT2 SUM",
            "title": "DAQ Temperature (oC)",
            "region": "Post Calibration Data",
            "column": 2,
            "hide": True,
            "column header": randStr+"CERTIFICATE:DAQ TEMP"
        }
        )

        retrieveData["Test Preferences"].append({
            "test": "FT2 SUM",
            "title": "Air2",
            "region": "Post Calibration Data",
            "column": 5,
            "hide": True,
            "column header": randStr+"CERTIFICATE:CALIB"
        }
        )
        for i in retrieveData["Test Preferences"]:
            if(i["test"] not in detectionList):
                raise Exception(
                    'One or more of the "Test Preferences" has an invalid "test" name')
            detectionList[i["test"]].append(i)

        

    except:
        raise Exception('No "Test Preferences" key in prefences file')

    genCert = "Generate Certificates" in retrieveData and retrieveData["Generate Certificates"]


def getSkippable(sn):
    global data, retrieveData
    skip = False
    if("Avoid" in retrieveData):
        for i in retrieveData["Avoid"]:
            if i not in data[sn]:
                continue
            if anyIn(data[sn][i], retrieveData["Avoid"][i]):
                skip = True
    if("Limit" in retrieveData):
        for i in retrieveData["Limit"]:
            if i not in data[sn]:
                skip = True
                continue
            if not anyIn(data[sn][i], retrieveData["Limit"][i]):
                skip = True
    try:
        if("Dates" in retrieveData):
            isIn = len(retrieveData["Dates"]) == 0
            for i in retrieveData["Dates"]:
                snDate = dateutil.parser.parse(data[sn]["Date"])
                snDate = {
                    "Day": snDate.day,
                    "Month": snDate.month,
                    "Year": snDate.year
                }
                if("Day" not in i):
                    del snDate["Day"]
                if("Month" not in i):
                    del snDate["Month"]
                if("Year" not in i):
                    del snDate["Year"]

                if(snDate == i):
                    isIn = True
            if(not isIn):
                skip = True
    except:
        pass
    return skip
