import csv
import glob
import os
import sys

from click import edit
from utils import editList
from tkinter import filedialog
from tkinter import *

dirs=""
outdir = "OUTPUT/"

if(sys.argv[1] == 'i'):
    root = Tk()
    root.withdraw()
    outdir = filedialog.askdirectory()+"/"
elif(sys.argv[1] == 'd'):
    with open("EOLT-Test-Analyzer/dirs.txt") as f:lines = f.readlines()
    if(len(lines)<2): raise Exception("\n\nInvalid saved directores. Try manually before re-attempting this method")
    outdir = lines[0]
    if(outdir[-1]=="\n") : outdir = outdir[0:-1]
    dirs = [lines[1]]
    for d in dirs:
        if(d[-1]=="\n") : d = d[0:-1]
else:
    outdir += "FACTORY\\"



def createFile():
    global dirs
    with open(outdir+outFileName, mode="w", newline='') as out:
        writer = csv.writer(out)
        # output header to csv
        writeHeaderToFile(writer)
        # get list of directories to run
        if len(sys.argv) > 1:
            if(sys.argv[1] == 'i'):
                root = Tk()
                root.withdraw()
                dirs = [filedialog.askdirectory()+"/"]
            elif(sys.argv[1] != 'd'): 
                dirs = sys.argv[1:]
        else:
            dirs = [os.getcwd()+"/TEST DATA/"]
        # dirs.insert(0, "baseline")
        # print(dirs)
        original = os.getcwd()
        editList(detectionList)
        print(dirs)

        for dir in dirs:
            os.chdir(dir)
            fileNames = glob.glob(globType, recursive=True)
            
            try:
                fileNames.sort(key=lambda x: x.split("_")[1] + x.split("_")[3] + x.
                               split("_")[4])
            except:
                pass
            writeDataToFile(writer, dir, fileNames)  # runs for every directory
            os.chdir(original)  # return to original dir

        writeSummaryToFile(writer)


if (len(sys.argv) < 2):
    print(
        "usage: python EOLT-Test-Analyzer/main.py <test directories>")
    exit()

from factory import *
createFile()



lines = ["",""]
lines[0] = outdir+("/" if outdir[-1]!="/" and outdir[-1]!="\\" else "")+"\n"
lines[1] = ' '.join([d+("/" if d[-1]!="/" and d[-1]!="\\" else "") for d in dirs])
print(lines)
with open("EOLT-Test-Analyzer/dirs.txt", "w") as f:f.writelines(lines)