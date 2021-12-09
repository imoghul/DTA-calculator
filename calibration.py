import csv, glob, os, sys
from numpy import mean

outFileName = "calibration results.csv"
globType = "**/*SUM*.csv"


def average(x):
    if len(x) == 0: return 0
    return mean(x)


def retrieveData(fileName):
    isReading = False
    with open(fileName, newline='') as file:
        for row in csv.reader(file, delimiter='\n', quotechar=','):
            for r in row:
                v = r.split(",")
                if (v[0] == "Calibration Data"): isReading = True
                if (v[0] == "Post Calibration Data"): isReading = False
                if (isReading and v[0] == "Air"):
                    if v[4] != '': return (float(v[4]))
                    elif v[1] != '': return 0
                    else: return None
        return None


def writeHeaderToFile(writer):
    header = [
        "Test", "Run", "Serial Number", "Offset", "Delta Offset to Baseline"
    ]
    # writer.writerow(header)


interests = ["VL212860020", "VL212880012", "VL212910026","FB6"]
baselineOffsets = {}
data = []


def writeDataToFile(writer, dir, fileNames):
    runs = {}
    for fileName in fileNames:
        outlist = [dir]
        try:
            offset = retrieveData(fileName)
            # check if a offset was retreived
            if offset == None: continue
            serialNum = fileName.split("_")[1]
            # check if serial number is one of the ones we are testing
            if not (serialNum in interests): continue
            test = dir
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
            outlist = [test, runs[serialNum], serialNum, offset, dbOffset]
            data.append(outlist)
            print(outlist)
        except:
            print(fileName + " couldn't be read")


def writeSummaryToFile(writer):
    serialNums = list(dict.fromkeys([x[2] for x in data]))
    tests = list(dict.fromkeys([x[0] for x in data]))
    # creater and write headers
    header = tests.copy()
    header += ["d_" + x for x in tests]
    header.insert(0, "Serial Number")
    header.insert(1, "Run")
    pdSetpoint = ["PD Setpoints: ", ""]
    for i in range(len(header)):
        pdSetpoint.append("")
    for i in range(2, len(header)):
        if "test4" in header[i]: pdSetpoint[i] = "10"
        elif "test5" in header[i]: pdSetpoint[i] = "0"
        elif "test6" in header[i]: pdSetpoint[i] = "-10"
        else: pdSetpoint[i] = "-18"
    writer.writerow(pdSetpoint)
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
            for _ in range(len(tests) * 2):
                l.append("")
            for t in tests:
                curr = None
                for i in testData[s]:
                    if i[0] == t and i[1] == r:
                        curr = i
                if curr == None: continue
                l[header.index(t)] = curr[2]
                l[header.index(t) + len(tests)] = curr[3]
            writer.writerow(l)