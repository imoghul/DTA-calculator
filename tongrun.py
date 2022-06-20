import csv
import glob
import os
import sys
from utils import *
import random
import string

randStr = (''.join(
    random.choice(string.ascii_lowercase + string.digits +
                  string.ascii_uppercase) for i in range(20)))
# + input("Output file Location (TONGRUN/): ")
outFileName = "TONGRUN/summary.csv"
globType = "**/*SUM*.csv"

data = {}

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
    with open(fileName, newline='') as file:
        for row in csv.reader(file, delimiter='\n', quotechar=','):
            for r in row:
                v = r.split(',')
                if("SN" in v or "Serial Number" in v):
                    data[v[1]] = {}
                    data[v[1]]["filename"] = fileName.split("\\")[-1]
                    continue



def writeHeaderToFile(writer):
    pass


def writeDataToFile(writer, dir, fileNames):
    counter = 0
    for fileName in fileNames:
        try:
            counter+=1
            if(counter>=100):return
            calc(fileName)
        except:
            print(fileName + " couldn't be read")


def writeSummaryToFile(writer):
    print(data)
    for i in range(10):
        pass# writer.writerow()
