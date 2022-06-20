import csv
import glob
import os
import sys
from utils import *

outFileName = "voltage results.csv"
globType = "**/*SUM*.csv"
detectionList = []

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
    vphp1 = None
    calib = None
    chamber = None
    initTemp = None
    finalTemp = None
    testResult = None
    isReadingCalib = False
    fileData = []
    with open(fileName, newline='') as file:
        for row in csv.reader(file, delimiter='\n', quotechar=','):
            for r in row:
                v = r.split(",")
                fileData.append(v)
                if (v[0] == "Calibration Data"):
                    isReadingCalib = True
                if (v[0] == "Post Calibration Data"):
                    isReadingCalib = False
                if (v[0] == "Init Temperature"):
                    initTemp = float(v[1])
                if (v[0] == "Final Temperature"):
                    finalTemp = float(v[1])
                if (v[0] == "TestResult"):
                    testResult = (v[1])
                if (v[0] == "PostCalCheck UUT Responses" and v[2] == "Vphp1"):
                    vphp1 = float(v[3])
                if (v[0] == "PostCalCheck UUT Responses"
                        and v[2] == "chamber"):
                    chamber = float(v[3])
                if isReadingCalib and v[0] == "Air":
                    if v[4] != '':
                        calib = (float(v[4]))
                    elif v[1] != '':
                        calib = 0
    testTypes = [x[0] for x in fileData]
    begin = testTypes.index("PullDown UUT Sampling Responses")
    end = len(testTypes) - 1
    testTime = readTime(fileData[end][1]) - readTime(fileData[begin][1])
    return vphp1, calib, chamber, testTime, initTemp, finalTemp, testResult


def writeHeaderToFile(writer):
    header = [
        "Test", "Serial Number", "Initial Temperature", "Final Temperature",
        "Test Duration", "Chamber Temperature at Calib.", "Voltage",
        "Test Result"
    ]
    writer.writerow(header)


def writeDataToFile(writer, dir, fileNames):
    for fileName in fileNames:
        try:
            serialNum = fileName.split("_")[1]
            (voltage, calib, chamber, testTime, initTemp, finalTemp,
             res) = retrieveData(fileName)
            writer.writerow([
                dir, serialNum, initTemp, finalTemp, testTime, chamber,
                voltage, res
            ])
        except:
            print(fileName + " couldn't be read")


def writeSummaryToFile(writer):
    pass
