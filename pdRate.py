import csv
import glob
import os
import sys
from utils import *

outFileName = "pulldown rate results.csv"
globType = "**/*RAW*.csv"


def readTime(dt):  # sample dt: 3:09:12.039 PM 11/24/2021
    dt = dt.split(" ")
    d = dt[2]
    d_arr = (d.split("/"))
    t = dt[0]
    year = int(d_arr[2])
    month = int(d_arr[0])
    day = int(d_arr[1])
    h = int(t.split(":")[0])
    m = int(t.split(":")[1])
    s = float(t.split(":")[2])
    if (dt[1] == "PM") & h != 12:
        h += 12
    if (dt[1] == "AM") & h == 12:
        h = 0
    return (year, month, day, h, m, s)


def calc(fileName):
    times = []
    temps = []
    roomTemps = []
    with open(fileName, newline='') as file:
        for row in csv.reader(file, delimiter='\n', quotechar=','):
            for r in row:
                v = r.split(',')
                if len(v) > 2 and v[5] == "Pre-PullDown":
                    temps.append(float(v[2]))
                    times.append(v[0])
                    roomTemps.append(float(v[3]))

    (startTemp, startInd) = closestTo(temps, 19)
    (endTemp, endInd) = closestTo(temps, 15)
    endTime = times[endInd]
    startTime = times[startInd]
    (y, mon, d, h, m, s) = readTime(startTime)
    start = dtToMin(y, mon, d, h, m, s)
    (y, mon, d, h, m, s) = readTime(endTime)
    end = dtToMin(y, mon, d, h, m, s)
    return ((startTemp-endTemp)/(end-start), average(roomTemps))


def writeHeaderToFile(writer):
    header = ["Test", "Serial Number", "Date", "Time",
              "Average Room Temperature", "PullDown Time"]
    writer.writerow(header)


def writeDataToFile(writer, dir, fileNames):
    for fileName in fileNames:
        outlist = [dir]
        try:
            (pdRate, roomTemp) = calc(fileName)
            filelist = fileName.split("_")
            outlist.append(filelist[1])
            if (len(filelist) >= 5):
                _date = filelist[len(filelist) - 3]
                d = _date[4:6] + "/" + _date[6:] + "/" + _date[0:4]
                outlist.append(d)
                t = filelist[len(filelist) - 2]
                t = t[0:2] + ":" + t[2:4] + ":" + t[4:6]
                outlist.append(t)
            else:
                outlist.append("")
                outlist.append("")
            outlist.append(roomTemp)
            outlist.append(pdRate)
            print(outlist)
            writer.writerow(outlist)
        except:
            print(fileName + " couldn't be read")


def writeSummaryToFile(writer):
    pass
    # writer.writerow([])
    # avgList = ["" for i in range(dtasToCalc+5)]
    # for i in range(dtasToCalc):
    #     avgList.append(round(average([d[i] for d in DTAs if len(d) > i]), 1))
    # writer.writerow(avgList)
