import csv, glob, os, sys
from utils import *

outFileName = "calibration results.csv"
globType = "**/*SUM*.csv"


def retrieveData(fileName):
    isReading = False
    offset = None
    setPoint = None
    with open(fileName, newline='') as file:
        for row in csv.reader(file, delimiter='\n', quotechar=','):
            for r in row:
                v = r.split(",")
                if (v[0] == "Calibration Data"): isReading = True
                if (v[0] == "Post Calibration Data"): isReading = False
                if (len(v)>3 and v[2] == "PrePullDownCheck_Setpoint -20C"): setPoint = float(v[3])
                if (isReading and v[0] == "Air"):
                    if v[4] != '': offset = (float(v[4]))
                    elif v[1] != '': offset = 0
                    else: offset == None
        return setPoint,offset


def writeHeaderToFile(writer):
    header = [
        "Test", "Run", "Serial Number", "Offset", "Delta Offset to Baseline"
    ]
    # writer.writerow(header)


interests = ["VL212860020", "VL212880012", "VL212910026", "FB6"]
baselineOffsets = {}
data = []


def writeDataToFile(writer, dir, fileNames):
    runs = {}
    for fileName in fileNames:
        outlist = [dir]
        try:
            setPoint,offset = retrieveData(fileName)
            # check if a offset was retreived
            if offset == None: continue
            serialNum = fileName.split("_")[1]
            # check if serial number is one of the ones we are testing
            if not (serialNum in interests): continue
            pdSp = str(setPoint)#dir
            # increment number of runs
            try:
                runs[serialNum] += 1
            except:
                runs[serialNum] = 1
            dbOffset = 0
            if (dir == "baseline"):
                baselineOffsets[serialNum] = offset
            else:
                try:  # delta baseline calculation
                    dbOffset = offset - baselineOffsets[serialNum]
                except:  # no baseline found
                    pass
            outlist = [pdSp, runs[serialNum], serialNum, offset, dbOffset]
            data.append(outlist)
            print(outlist,dir)
        except:
            print(fileName + " couldn't be read")


def writeSummaryToFile(writer):
    serialNums = list(dict.fromkeys([x[2] for x in data]))
    pdSps = list(dict.fromkeys([x[0] for x in data]))
    # creater and write headers
    header = pdSps.copy()
    header += ["d_" + x for x in pdSps]
    header.insert(0, "Serial Number")
    header.insert(1, "Run")
    writer.writerow(header)
    # retrieve data and store in dict of key:serial# and data:[test run offset dboffset]
    testData = {}
    for s in serialNums:
        testData[s] = []
        for d in data:
            if d[2] == s:
                testData[s].append([d[0], d[1], d[3], d[4]])

    for s in testData:
        runs = max([x[1] for x in testData[s]])
        for r in range(1, 1 + runs):
            l = [s, r]
            for _ in range(len(pdSps) * 2):
                l.append("")
            for sp in pdSps:
                curr = None
                for i in testData[s]:
                    if i[0] == sp and i[1] == r:
                        curr = i
                if curr == None: continue
                l[header.index(sp)] = curr[2]
                l[header.index(sp) + len(pdSps)] = curr[3]
            writer.writerow(l)
