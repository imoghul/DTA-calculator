from audioop import add
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

daqTempKey = (''.join(random.choice(string.ascii_lowercase +
              string.digits + string.ascii_uppercase) for i in range(20)))
calibKey = daqTempKey
while calibKey == daqTempKey:
    calibKey = (''.join(random.choice(string.ascii_lowercase +
                string.digits + string.ascii_uppercase) for i in range(20)))
testResKey = calibKey
while testResKey == calibKey:
    testResKey = (''.join(random.choice(string.ascii_lowercase +
                                        string.digits + string.ascii_uppercase) for i in range(20)))
# daqTempKey = "daqTempKey"
# calibKey = "calibKey"
# testResKey = "testResKey"

dirNum = 0

isThreading = True
threads = []
processing = []
max = 5000
threadCount = 0

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
errors = []


def calc(fileName, dud):
    global currentSN, data, headers, errors
    try:
        fileType = getFileType(fileName)

        if(fileType == "FT2 SUM"):
            with open(fileName, newline='') as file:
                sn = None
                region = ""
                for row in csv.reader(file, delimiter='\n', quotechar=','):
                    for r in row:
                        v = r.split(',')
                        if("SN" in v or "Serial Number" in v):
                            sn = v[1]
                            currentSN = sn
                            if(sn not in data):
                                data[sn] = {}  # data[sn] = {}
                            if(fileName not in data[sn]):
                                data[sn][fileName] = {}
                            else:break
                            _date = fileName.replace(".csv", "").split("_")
                            index = 1
                            for i in range(len(_date)):
                                if("SUM" in _date[i]):
                                    index = i
                            _date = _date[index-2]
                            data[sn][fileName]["Serial Number"] = sn
                            # addToData(data[sn], "Serial Number", sn, sn)
                            data[sn][fileName]["FT2 SUM:Date"] = _date[4:6]+"/"+_date[6:8]+"/"+_date[0:4]
                            # addToData(data[sn], "FT2 SUM:Date",
                                    # _date[4:6]+"/"+_date[6:8]+"/"+_date[0:4], sn)
                            data[sn][fileName]["FT2 SUM:File Name"] = fileName.split("\\")[-1]
                            # addToData(data[sn], "FT2 SUM:File Name",
                            #         fileName.split("\\")[-1], sn)
                            continue
                        elif sn == None:
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
                                    data[sn][fileName][dataKey] = v[index]
                                    # addToData(data[sn], dataKey, v[index], sn)
                                elif dataRegion != None and (dataField in v and region == dataRegion):
                                    data[sn][fileName][dataKey] = v[index] if v[index] != "" else "0"
                                    if(sn=="TR1562152124" and dataKey=="Calib:Air2"):
                                        _=5#print(fileName)
                                    # addToData(
                                        # data[sn], dataKey, v[index] if v[index] != "" else "0", sn)

                                
                            elif type(dataField) == list:
                                allIn = all([i in v for i in dataField])
                                if dataRegion == None and allIn:
                                    data[sn][fileName][dataKey] = v[index]
                                    # addToData(data[sn], dataKey, v[index], sn)
                                elif dataRegion != None and (allIn and region == dataRegion):
                                    data[sn][fileName][dataKey] = v[index] if v[index] != "" else "0"
                                    # addToData(
                                    #     data[sn], dataKey, v[index] if v[index] != "" else "0", sn)
                                
                    
                if(sn == None):
                    raise Exception(
                        "Doesn't have a serial number")
        elif(fileType == "FT3"):
            with open(fileName, newline='') as file:
                _date = "couldn't parse"
                try:
                    _date = v[ft3headers.index("TimeStamp")].split(" ")[
                        0]
                except:
                    pass
                ft3headers = None
                sn = None
                for row in csv.reader(file, delimiter='\n', quotechar=','):
                    for r in row:
                        v = r.split(',')
                        if(ft3headers == None):
                            ft3headers = v
                        else:
                            sn = v[ft3headers.index("Serial Number")]
                            if(sn not in data):
                                data[sn] = {}
                            if(fileName not in data[sn]):
                                data[sn][fileName] = {}
                            data[sn][fileName]["Serial Number"] = sn
                            # addToData(data[sn], "Serial Number", sn, sn)
                            for i in detectionList["FT3"]:
                                title = getTitle_config(i)
                                dataField = i["title"]
                                if(dataField in ft3headers):
                                    try:
                                        data[sn][fileName][title] = v[ft3headers.index(title)]
                                        # addToData(
                                        #     data[sn], title, v[ft3headers.index(dataField)], sn)
                                    except:
                                        pass
                            data[sn][fileName]["FT3:File Name"] = fileName.split("\\")[-1]
                            # addToData(data[sn], "FT3:File Name",
                            #           fileName.split("\\")[-1], sn)
                            data[sn][fileName]["FT3:Date"] = v[ft3headers.index("TimeStamp")].split(" ")[0]
                            # addToData(data[sn], "FT3:Date", _date, sn)
                
        elif(fileType == "FT1"):
            with open(fileName, newline='') as file:
                sn = None
                ft1headers = None
                modelId = None
                for row in csv.reader(file, delimiter='\n', quotechar=','):
                    for r in row:
                        v = r.split(',')
                        if("Model ID" in v and len(v) > 1):
                            modelId = v[1]
                        if("SN" in v or "Serial Number" in v):
                            sn = v[1]
                            currentSN = sn
                            if(sn not in data):
                                data[sn] = {}
                            if(fileName not in data[sn]):
                                data[sn][fileName] = {}
                            data[sn][fileName]["Serial Number"] = sn
                            # addToData(data[sn], "Serial Number", sn, sn)
                            data[sn][fileName]["FT1:File Name"] = fileName.split("\\")[-1]
                            # addToData(data[sn], "FT1:File Name",
                                    # fileName.split("\\")[-1], sn)
                            _date = fileName.replace(".csv", "").split("_")[-2]
                            data[sn][fileName]["FT1:Date"] = _date[2:4] + "/"+_date[4:6]+"/20"+_date[0:2]
                            # addToData(data[sn], "FT1:Date", _date[2:4] +
                            #         "/"+_date[4:6]+"/20"+_date[0:2], sn)
                            continue
                        elif sn == None:
                            continue
                        if(len(v) > 2 and ft1headers == None):
                            ft1headers = v
                        for i in detectionList["FT1"]:
                            try:
                                dataField = i["title"]
                                dataKey = getTitle_config(i)
                            except:
                                raise Exception(
                                    "One or more required keys in an FT1 preference are missing")

                            if(ft1headers == None):
                                if(dataField == "Model ID" and modelId != None):
                                    data[sn][fileName][dataKey] = modelId
                                    # addToData(data[sn], dataKey, modelId, sn)
                                elif(dataField in v):
                                    data[sn][fileName][dataKey] = v[1]
                                    # addToData(data[sn], dataKey, v[1], sn)
                            elif "step" in i:
                                step = i["step"]
                                if(v[0] == step and dataField in ft1headers):
                                    data[sn][fileName][dataKey] = v[ft1headers.index(dataField)]
                                    # addToData(
                                    #     data[sn], dataKey, v[ft1headers.index(dataField)], sn)

                if(sn == None):
                    raise Exception("Doesn't have a serial number")
        elif(fileType == "FT2 RAW"):
            return False
        return True
    except csv.Error as e:
        pass
    except Exception as e:
        errors.append(
            fileName + " couldn't be read with the following error: "+str(e))
        pass
        # print(fileName + " couldn't be read with the following error: "+str(e))


def writeHeaderToFile(writer):
    # check for duplicates
    check = []
    duplicates = []
    dups = False
    for test in detectionList:
        for i in detectionList[test]:
            title = getTitle_config(i)
            if title not in check:
                check.append(title)
            else:
                if(title not in duplicates):
                    duplicates.append(title)
                dups = True

    if(dups):
        print("Be cautious of using duplicate headers, this may cause overwriting data:")
        for i in duplicates:
            print(i)
        print()
        # raise Exception(
        #     "Cannot have duplicates in header. Please check your preferences.json and resolve issue. If there are not issues run the script again")


def writeDataToFile(writer, dir, fileNames):
    global dirNum, threads, processing, max, threadCount
    dirNum += 1
    counter = 0
    length = len(fileNames)
    global certdir
    for fileName in fileNames:
        counter += 1
        ###
        if(not isThreading):
            process_bar("Retrieving from the %s directory" %
                        ordinal(dirNum), counter, length)
            success = calc(fileName, 0)
        ###
        if(isThreading):
            process_bar("Initializing for the %s directory" %
                        ordinal(dirNum), counter, length)
            threads.append(threading.Thread(target=calc, args=(fileName, 0)))
        ###
        if(counter > length):
            return
    counter = 0


def writeSummaryToFile(writer):
    global data, threads, processing, max, threadCount

    # execute threads

    if(isThreading):
        import time
        start = time.time()
        runThreads(threads,2000,"Retrieving Data")
        print("Retrieved in "+str(time.time()-start)+" seconds")
    # with open(certdir+f'/data{"Thread" if isThreading else "Normal"}.json', "w") as f:
    #     json.dump(data, f)

    # sort data
    print("Attempting to sort by date")
    try:
        data = {k: v for k, v in sorted(data.items(), key=lambda sn: datetime.strptime(
            str(dateutil.parser.parse(sn[1]["FT2 SUM:Date"])), "%Y-%m-%d %H:%M:%S"))}
    except:
        pass  # print("Bad date exists, will not sort by date")
    # header calculating
    counter = 0
    length = len(data)
    global headers
    for sn in data:
        counter += 1
        process_bar("Processing Data", counter, length)
        for test in data[sn]:
            for header in data[sn][test]:
                if header not in headers:
                    headers.append(header)
    for i in reversed([getTitle_config(j) for j in detectionList["FT3"]]):
        moveToBeginning(headers, i)
    for i in reversed([getTitle_config(j) for j in detectionList["FT2 SUM"]]):
        moveToBeginning(headers, i)
    for i in reversed([getTitle_config(j) for j in detectionList["FT1"]]):
        moveToBeginning(headers, i)
    moveToBeginning(headers, "FT3:File Name")
    moveToBeginning(headers, "FT2 SUM:File Name")
    moveToBeginning(headers, "FT1:File Name")
    moveToBeginning(headers, "FT3:Date")
    moveToBeginning(headers, "FT2 SUM:Date")
    moveToBeginning(headers, "FT1:Date")
    moveToBeginning(headers, "Serial Number")
    for test in detectionList:
        for pref in detectionList[test]:
            if "hide" in pref and pref["hide"]:
                title = getTitle_config(pref)
                if title in headers:
                    headers.remove(title)
    writer.writerow(headers)
    # writing data
    counter = 0
    length = len(data)
    for sn in data:
        counter += 1
        process_bar("Writing Data", counter, length)
        for test in data[sn]:
            if(sn=="TR1562152124"):print(data[sn][test])
            for h in headers:
                if(h not in data[sn][test]):
                    data[sn][test][h] = " "  # "doesn't exist"

            if getSkippable(data[sn][test]):
                continue
            try:
                writer.writerow([data[sn][test][h] for h in headers])
            except:
                pass
                # print("Couldn't write data for %s, Most likely due to non encodable characters in filename"%sn)
            try:
                if(genCert and "FT2 SUM:Date" in data[sn][test] and testResKey in data[sn][test] and daqTempKey in data[sn][test] and calibKey in data[sn][test]):
                    createCertificate(sn, data[sn][test]["FT2 SUM:Date"], "Pass" if data[sn][test]
                                      [testResKey] == "Test Complete" else "Fail", data[sn][test][daqTempKey] if daqTempKey in data[sn][test] else "N/A", data[sn][test][calibKey] if calibKey in data[sn][test] else "N/A", certdir)
            except:
                raise Exception(
                    "Couldn't generate certificate, check config file for correct preferences")
    if("PDF Certificates" in retrieveData and retrieveData["PDF Certificates"] == True and "Generate Certificates" in retrieveData and retrieveData["Generate Certificates"] == True):
        convertToPDF_path(certdir)
    if(errors!=[]):
        print("\nErrors: ")
        for i in errors:
            print(i)


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
        print("Invalid preferences JSON file, check syntax: "+str(e))
        exit()

    try:
        retrieveData["Test Preferences"].append({
            "test": "FT2 SUM",
            "title": "DAQ Temperature (oC)",
            "region": "Post Calibration Data",
            "column": 2,
            "hide": True,
            "column header": daqTempKey
        }
        )
        retrieveData["Test Preferences"].append({
            "test": "FT2 SUM",
            "title": "Air2",
            "region": "Post Calibration Data",
            "column": 5,
            "hide": True,
            "column header": calibKey
        }
        )
        retrieveData["Test Preferences"].append({
            "test": "FT2 SUM",
            "title": "TestResult",
            "column": 2,
            "hide": True,
            "column header": testResKey
        }
        )

        for i in retrieveData["Test Preferences"]:
            if("test" not in i):
                raise Exception(
                    "One or more of the \"Test Preferences\" don't contain a \"test\"")
            elif(i["test"] not in detectionList):
                raise Exception(
                    'One or more of the "Test Preferences" has an invalid "test" name')
            detectionList[i["test"]].append(i)

    except:
        raise Exception('No "Test Preferences" key in prefences file')

    genCert = "Generate Certificates" in retrieveData and retrieveData["Generate Certificates"]


def getSkippable(row):
    global retrieveData
    skip = False

    if("Limit" in retrieveData):
        limFound = None
        if(type(retrieveData["Limit"]) != list):
            retrieveData["Limit"] = [retrieveData["Limit"]]
        if(len(retrieveData["Limit"]) and type(retrieveData["Limit"][0]) == dict):
            for i in retrieveData["Limit"]:  # looping through list of limits
                curr = []  # checks if the current key is fully part of said data field
                for lim in i:  # looping through keys in limits
                    if(limFound == None):
                        limFound = False
                    if lim not in row:
                        # if the current is not in the data fields then it doesn't need to be limited, therefore it is not fully part of the data field
                        curr.append(False)
                    else:
                        curr.append(allIn(row[lim], i[lim]))
                    if(not all(curr)):
                        break  # if the current key is not fully in the data field, then it doesn't need to be limited
                if(all(curr)):
                    limFound = True
            if(limFound == False):
                skip = True

    if("Avoid" in retrieveData):
        if(type(retrieveData["Avoid"]) != list):
            retrieveData["Avoid"] = [retrieveData["Avoid"]]
        if(len(retrieveData["Avoid"]) and type(retrieveData["Avoid"][0]) == dict):
            skipAv = False
            for i in retrieveData["Avoid"]:  # looping through list of avoids
                if(not skipAv):
                    curr = []  # checks if the current key is fully part of said data field
                    for av in i:  # looping through keys in avoids
                        if av not in row:
                            # if the current is not in the data fields then it doesn't need to be avoided, therefore it is not fully part of the data field
                            curr.append(False)
                        else:
                            curr.append(allIn(row[av], i[av]))
                        if(not all(curr)):
                            break  # if the current key is not fully in the data field, then it doesn't need to be avoided
                    if(all(curr) and curr != []):
                        skipAv = True
                if(skipAv):
                    skip = True
                    break

    try:
        if("Dates" in retrieveData):
            isIn = len(retrieveData["Dates"]) == 0
            for i in retrieveData["Dates"]:
                snDate = dateutil.parser.parse(row[i["test"]+":Date"])
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
