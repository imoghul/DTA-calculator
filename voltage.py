import csv, glob, os, sys
from numpy import mean

outFileName = "voltage results.csv"
globType = "**/*SUM*.csv"

dtToMin = lambda y, mon, d, h, m, s: (525600 * y + 43800 * mon + 1440 * d + 60
                                      * h + m + s / 60)


def average(x):
    if len(x) == 0: return 0
    return mean(x)


def readTime(dt):  # sample: 2021-12-09T15:55:31.235
    dt = dt.split("T")
    d = dt[0]
    t = dt[1]
    d = d.split("-")
    t = t.split(":")
    y = int(d[0])
    mon = int(d[2])
    d = int(d[1])
    h = int(t[0])
    m = int(t[1])
    s = float(t[2])
    return dtToMin(y, mon, d, h, m, s)


def retrieveData(fileName):
    if (fileName.find("_F_") != -1): pf="Fail"
    else:pf="Pass"
    vphp1 = None
    calib = None
    chamber = None
    initTemp = None
    finalTemp = None
    isReadingCalib = False
    fileData = []
    with open(fileName, newline='') as file:
        for row in csv.reader(file, delimiter='\n', quotechar=','):
            for r in row:
                v = r.split(",")
                fileData.append(v)
                if (v[0] == "Calibration Data"): isReadingCalib = True
                if (v[0] == "Post Calibration Data"): isReadingCalib = False
                if (v[0] == "Init Temperature"): initTemp = float(v[1])
                if (v[0] == "Final Temperature"): finalTemp = float(v[1])
                if (v[0] == "PostCalCheck UUT Responses" and v[2] == "Vphp1"):
                    vphp1 = float(v[3])
                if (v[0] == "PostCalCheck UUT Responses"
                        and v[2] == "chamber"):
                    chamber = float(v[3])
                if isReadingCalib and v[0] == "Air":
                    if v[4] != '': calib = (float(v[4]))
                    elif v[1] != '': calib = 0
    testTypes = [x[0] for x in fileData]
    begin = testTypes.index("PullDown UUT Sampling Responses")
    end = len(testTypes) - 1
    testTime = readTime(fileData[end][1]) - readTime(fileData[begin][1])
    return vphp1, calib, chamber, testTime, initTemp, finalTemp,pf


def writeHeaderToFile(writer):
    header = ["Test","Serial Number","Initial Temperature","Final Temperature","Test Duration","Chamber Temperature at Calib.","Voltage","Pass/Fail"]
    writer.writerow(header)


interests = ["VL212860020", "VL212880012", "VL212910026", "FB6"]
data = []


def writeDataToFile(writer, dir, fileNames):
    runs = {}
    for fileName in fileNames:
        outlist = [dir]
        try:
            serialNum = fileName.split("_")[1]
            (voltage,calib,chamber,testTime,initTemp,finalTemp,pf) = retrieveData(fileName)
            writer.writerow([dir,serialNum,initTemp,finalTemp,testTime,chamber,voltage,pf])
        except:
            print(fileName + " couldn't be read")


def writeSummaryToFile(writer):
    pass
