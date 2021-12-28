import csv, glob, os, sys
from utils import *
import random,string

randStr = (''.join(random.choice(string.ascii_lowercase+string.digits+string.ascii_uppercase) for i in range(20)))
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

def fixDupl(arr):
    common = [i for i in arr if arr.count(i)>1]
    for val in common:
        temp = 1
        for i in range(len(arr)):
            if arr[i]==val:
                arr[i]+=randStr+str(temp)+"(%d)"%temp
                temp+=1
    return(arr)

def calc(fileName):
    titles = []
    vals = []
    res = {}
    PrePulldownUUTResponses_started = None
    PostCalCheckUUTResponses_started = None
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
                    titles.append(v[0])
                    vals.append(v[1] if len(v)>1 else "")
                if(v[0] == "PrePullDown UUT Responses"):
                    if PrePulldownUUTResponses_started==None: PrePulldownUUTResponses_started = True
                    if PrePulldownUUTResponses_started==True:
                        titles.append("PrePullDown UUT Responses -->")
                        vals.append("|")
                        PrePulldownUUTResponses_started = False
                    titles.append(v[2])
                    vals.append(v[3])
                if(v[0] == "PostCalCheck UUT Responses"):
                    if PostCalCheckUUTResponses_started==None: PostCalCheckUUTResponses_started = True
                    if PostCalCheckUUTResponses_started==True:
                        titles.append("PostCalCheck UUT Responses -->")
                        vals.append("|")
                        PostCalCheckUUTResponses_started = False
                    titles.append(v[2])
                    vals.append(v[3])
                if(inCal and v[0]=="Air" and v[5]=="TRUE"):offset = 0
                if(inPostCal and v[0]=="Air" and offset==-1): offset = float(v[2])
        titles.append("offset")
        titles = fixDupl(titles)
        vals.append(offset)
        for i in range(len(titles)):res[titles[i]]=vals[i]
    return res

def writeHeaderToFile(writer):
    pass


def writeDataToFile(writer, dir, fileNames):
    for fileName in fileNames:
        try:
            d = calc(fileName)
            d["File Name"]=fileName
            data.append(d)
        except:
           print(fileName + " couldn't be read")

def writeSummaryToFile(writer):
    keys = []
    header = ["File Name"]
    for i in data:keys+=list(i.keys())
    for i in keys:
        if i not in header: header.append(i)
    writer.writerow([i if i.find(randStr)==-1 else i[0:i.find(randStr)] for i in header])
    for d in data:
        outlist = ["" for i in range(len(header))]
        headers = list(d.keys())
        for h in headers: outlist[header.index(h)]=d[h]
        writer.writerow(outlist)
