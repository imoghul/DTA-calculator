import csv
import glob
import os
import sys
from utils import *
import random
import string
from tqdm import tqdm

randStr = (''.join(
    random.choice(string.ascii_lowercase + string.digits +
                  string.ascii_uppercase) for i in range(20)))
outFileName = "long_summary"#"SUMMARY/" + input("Output file Location (SUMMARY/): ")
globType = "**/*SUM*.csv"
detectionList = []
data = []


def fixDupl(arr):
    common = [i for i in arr if arr.count(i) > 1]
    for val in common:
        temp = 1
        for i in range(len(arr)):
            if arr[i] == val:
                arr[i] += randStr + str(temp) + "(%d)" % temp
                temp += 1
    return (arr)


def calc(fileName):
    titles = []
    vals = []
    res = {}
    PrePulldownUUTResponses_started = None
    PostCalCheckUUTResponses_started = None
    inCal = False
    inPostCal = False
    offset = -1
    offsetFrom = ""
    # print(fileName)
    with open(fileName, newline='') as file:
        for row in csv.reader(file, delimiter='\n', quotechar=','):
            for r in row:
                v = r.split(',')
                if (v[0] == "Calibration Data"):
                    inCal = True
                if (v[0] == "Post Calibration Data"):
                    inCal = False
                    inPostCal = True
                if (v[0] == "UUT Responses"):
                    inPostCal = False
                if (v[0] in [
                        "SN", "TestResult", "Init Temperature",
                        "PullDown Starting Temperature", "Final Temperature", "Cooling Time (s)"
                ]):
                    titles.append(v[0])
                    vals.append(v[1] if len(v) > 1 else "")
                if (v[0] == "PrePullDown UUT Responses"):
                    if PrePulldownUUTResponses_started == None:
                        PrePulldownUUTResponses_started = True
                    if PrePulldownUUTResponses_started == True:
                        titles.append("PrePullDown UUT Responses -->")
                        vals.append("|")
                        PrePulldownUUTResponses_started = False
                    titles.append(v[2])
                    vals.append(v[3])
                if (v[0] == "PostCalCheck UUT Responses"):
                    if PostCalCheckUUTResponses_started == None:
                        PostCalCheckUUTResponses_started = True
                    if PostCalCheckUUTResponses_started == True:
                        titles.append("PostCalCheck UUT Responses -->")
                        vals.append("|")
                        PostCalCheckUUTResponses_started = False
                    titles.append(v[2])
                    vals.append(v[3])
                if (inCal and v[0] == "Air" and v[5] == "TRUE"):
                    offset = 0
                if (inPostCal and v[0] == "Air" and offset == -1):
                    offset = float(v[2])
        if offset != -1:
            titles.append("Offset")
        titles = fixDupl(titles)
        vals.append(offset)
        for i in range(len(titles)):
            res[titles[i]] = vals[i]
    # print(res)
    return res


def writeHeaderToFile(writer):
    pass


def writeDataToFile(writer, dir, fileNames):
    for fileName in tqdm(fileNames):
        try:
            d = calc(fileName)
            order = ("\\".join(fileName.split("\\")[0:-1]))
            d["Order"] = order
            filelist = fileName.split("_")
            if (len(filelist) >= 5):
                _date = filelist[len(filelist) - 3]
                dat = _date[4:6] + "/" + _date[6:] + "/" + _date[0:4]
                tim = filelist[len(filelist) - 2]
                tim = tim[0:2] + ":" + tim[2:4] + ":" + tim[4:6]
            else:
                dat = ""
                tim = ""
            d["Date"] = dat
            d['Time'] = tim
            data.append(d)
        except:
            print(fileName + " couldn't be read")


def writeSummaryToFile(writer):
    keys = []
    header = ["Order", "Date", "Time"]
    temp = data.copy()
    temp.sort(reverse=True, key=lambda x: len(x.keys()))
    for i in temp:
        keys = list(i.keys())
        for i in keys:
            if i not in header:
                header.append(i)
    writer.writerow(
        [i if i.find(randStr) == -1 else i[0:i.find(randStr)] for i in header])
    for d in data:
        outlist = ["" for i in range(len(header))]
        headers = list(d.keys())
        for h in headers:
            outlist[header.index(h)] = d[h]
        writer.writerow(outlist)


def transfer(cdir, pdir, odir, log):pass