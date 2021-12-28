import csv, glob, os, sys
from utils import *
import random,string

randStr = (''.join(random.choice(string.ascii_lowercase+string.digits+string.ascii_uppercase) for i in range(20)))
tutFileName = "SUMMARY/summary mvt totes.csv"
globType = "**/*SUM*.csv"

data=[]
smartSheetSNs="VL212460001,VL212460002,VL212460003,VL212460004,VL212460005,VL212460006,VL212510001,VL212510002,VL212510003,VL212510004,VL212510005,VL212510006,VL212510007,VL212510008,VL212510009,VL212510010,VL212510011,VL212510012,VL212590009,VL212590010,VL212590014,VL212590016,VL212590017,VL212590018,VL212590019,VL212650001,VL212650002,VL212650003,VL212650004,VL212650005,VL212650008,VL212660011,VL212660012,VL212780001,VL212780002,VL212780003,VL212780004,VL212780005,VL212800001,VL212800002,VL212800003,VL212800004,VL212800005,VL212800006,VL212800007,VL212800008,VL212800009,VL212800011,VL212800012,VL212800013,VL212860001,VL212860002,VL212860003,VL212860004,VL212860005,VL212860006,VL212860007,VL212860008,VL212860009,VL212860010,VL212860011,VL212860012,VL212860013,VL212860015,VL212860016,VL212860019,VL212860020,VL212860021,VL212860022,VL212860023,VL212860024,VL212860025,VL212880001,VL212880002,VL212880003,VL212880004,VL212880005,VL212880006,VL212880007,VL212880008,VL212880009,VL212880010,VL212880011,VL212880012,VL212880013,VL212880014,VL212880015,VL212880016,VL212880018,VL212880019,VL212910021,VL212910022,VL212910025,VL212910026,VL212910027,VL212910028,VL212910029,VL212910030"

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
    offsetFrom = ""
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
                    if v[0]=="SN":
                        titles.append("In SmartSheet")
                        vals.append("TRUE" if v[1] in smartSheetSNs else "FALSE")
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
                if(inCal and v[0]=="Air" and v[5]=="TRUE"):
                    offset = 0
                if(inPostCal and v[0]=="Air" and offset==-1):
                    offset = float(v[2])
        if offset!=-1:titles.append("Offset")
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
            order = ("\\".join(fileName.split("\\")[0:-1]))
            d["Order"] = order
            filelist = fileName.split("_")
            if (len(filelist) >= 5):
                _date = filelist[len(filelist) - 3]
                date = _date[4:6] + "/" + _date[6:] + "/" + _date[0:4]
                time = filelist[len(filelist) - 2]
                time = time[0:2] + ":" + time[2:4] + ":" + time[4:6]
            else:
                date = ""
                time = ""
            d["Date"] = date
            d['Time'] = time
            data.append(d)
        except:
           print(fileName + " couldn't be read")

def writeSummaryToFile(writer):
    keys = []
    header = ["Order","Date","Time"]
    temp = data.copy()
    temp.sort(reverse = True,key = lambda x:len(x.keys()))
    for i in temp:
        keys=list(i.keys())
        for i in keys:
            if i not in header: header.append(i)
    writer.writerow([i if i.find(randStr)==-1 else i[0:i.find(randStr)] for i in header])
    for d in data:
        outlist = ["" for i in range(len(header))]
        headers = list(d.keys())
        for h in headers: outlist[header.index(h)]=d[h]
        writer.writerow(outlist)
