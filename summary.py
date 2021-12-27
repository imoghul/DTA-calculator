import csv, glob, os, sys
from utils import *

outFileName = "summary.csv"
globType = "**/*SUM*.csv"

data=[]

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
    res={}
    PrePulldownUUTResponses_started = False
    PostCalCheckUUTResponses_started = False
    inCal = False
    inPostCal = False
    offset = -1
    with open(fileName, newline='') as file:
        for row in csv.reader(file, delimiter='\n', quotechar=','):
            for r in row:
                v = r.split(',')
                if(v[0] == "Calibration Data"):inCal = True
                if(v[0] == "Post Calibration Data"):
                    inCal = False
                    inPostCal = True
                if(v[0] == "UUT Responses"): inPostCal = False
                if(v[0] in ["SN","TestResult","Init Temperature","PullDown Starting Temperature","Final Temperature"]):
                    res[v[0]] = v[1] if len(v)>1 else ""
                if(v[0] == "PrePullDown UUT Responses"):
                    if not PrePulldownUUTResponses_started: PrePulldownUUTResponses_started = True
                    if PrePulldownUUTResponses_started: res["PrePullDown UUT Responses -->"] = "|"
                    res[v[2]] = v[3]
                if(v[0] == "PostCalCheck UUT Responses"):
                    if not PostCalCheckUUTResponses_started: PostCalCheckUUTResponses_started = True
                    if PostCalCheckUUTResponses_started: res["PostCalCheck UUT Responses -->"] = "|"
                    res[v[2]] = v[3]
                if(inCal and v[0]=="Air" and v[5]=="TRUE"):offset = 0
                if(inPostCal and v[0]=="Air" and offset==-1): offset = float(v[2])
        res["offset"]=offset
    return res

def writeHeaderToFile(writer):
    pass


def writeDataToFile(writer, dir, fileNames):
    for fileName in fileNames:
        try:
            d = calc(fileName)
            d["File Name"] = fileName
            data.append(d)
        except:
            print(fileName + " couldn't be read")

def writeSummaryToFile(writer):
    keys = []
    header = ["File Name"]
    for i in data:keys+=list(i.keys())
    for i in keys:
        if i not in header: header.append(i)
    writer.writerow(header)
    for d in data:
        outlist = ["" for i in range(len(header))]
        keys = list(d.keys())
        for k in keys:
            outlist[header.index(k)] = d[k]
        writer.writerow(outlist)
