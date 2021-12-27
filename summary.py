import csv, glob, os, sys
from utils import *

outFileName = "pulldown rate results.csv"
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
    with open(fileName, newline='') as file:
        for row in csv.reader(file, delimiter='\n', quotechar=','):
            for r in row:
                v = r.split(',')
                if(v[0]=="SN"):
                  res[v[0]] = v[1]
    return res

def writeHeaderToFile(writer):
    pass


def writeDataToFile(writer, dir, fileNames):
    for fileName in fileNames:
        outlist = [fileName]
        print(outlist)
        calc(fileName)
        # try:
        #     data.append(calc(fileName))
        # except:
        #     print(fileName + " couldn't be read")
    print(data)

def writeSummaryToFile(writer):
    pass