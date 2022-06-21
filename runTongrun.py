import csv
import glob
import os
import sys

from click import edit
from utils import editList
from tkinter import filedialog
from tkinter import *


outdir = "CSV OUTPUT/"
if(sys.argv[1] == 'i'):
    root = Tk()
    root.withdraw()
    outdir = filedialog.askdirectory()+"/"
else:
    outdir += "TONGRUN\\"

print(outdir)


def createFile():
    with open(outdir+outFileName, mode="w", newline='') as out:
        writer = csv.writer(out)
        # output header to csv
        writeHeaderToFile(writer)
        # get list of directories to run
        if len(sys.argv) > 1:
            if(sys.argv[1] == 'i'):
                root = Tk()
                root.withdraw()
                dirs = [filedialog.askdirectory()]
            else: dirs = sys.argv[1:]
        else:
            dirs = [os.getcwd()+"/TEST DATA/"]
        # dirs.insert(0, "baseline")
        # print(dirs)
        original = os.getcwd()
        editList(detectionList)
        
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

from tongrun import *
createFile()

