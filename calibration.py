import csv, glob, os, sys
from numpy import mean

outFileName="calibration results.csv"
globType="**/*SUM*.csv"


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
                    else: return None
        return None

interests = ["VL212860020","VL212880012","VL212910026"]
baselineOffsets = {}

def writeHeaderToFile(writer):
  header = [
      "Test", "Run", "Serial Number", "Offset", "Delta Offset to Baseline"
  ]
  writer.writerow(header)
def writeDataToFile(writer,dir,fileNames):
    runs = {}
    for fileName in fileNames:
        outlist = [dir]
        try:
            offset = retrieveData(fileName)
            serialNum = fileName.split("_")[1]
            if not (serialNum in interests): continue
            test = dir
            # check if a offset was retreived
            if offset == None: continue
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
            print(outlist)
            writer.writerow(outlist)
        except:
            print(fileName + " couldn't be read")

def writeSummaryToFile(writer):
  pass
