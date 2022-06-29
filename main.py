import csv
import glob
import os
import sys

from click import edit
from tkinter import filedialog
from tkinter import *


outdir = "L:/Engineering_Services/Public/EOLT/Factory Data - Vexos Ohio/Summary"
if(sys.argv[2] == 'i'):
    root = Tk()
    root.withdraw()
    outdir = filedialog.askdirectory()


def createFile():
    with open(outdir+"\\"+outFileName, mode="w", newline='') as out:
        writer = csv.writer(out)
        # output header to csv
        writeHeaderToFile(writer)
        # get list of directories to run
        if len(sys.argv) > 2:
            if(sys.argv[2] == 'i'):
                root = Tk()
                root.withdraw()
                dirs = [filedialog.askdirectory()]
            else: dirs = sys.argv[2:]
        else:
            dirs = [os.getcwd()+"/TEST DATA/"]
        # dirs.insert(0, "baseline")
        # print(dirs)
        original = os.getcwd()
        print(outFileName)
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
        "usage: python EOLT-Test-Analyzer/main.py [d/c/v/p/s] <test directories>")
    exit()
elif (sys.argv[1] == "d"):
    from dta import *
    createFile()
elif (sys.argv[1] == "c"):
    from calibration import *
    createFile()
elif (sys.argv[1] == "v"):
    from voltage import *
    createFile()
elif (sys.argv[1] == "p"):
    from pdRate import *
    createFile()
elif (sys.argv[1] == "s"):
    from summary import *
    createFile()
else:
    from calibration import *
    createFile()
    from dta import *
    createFile()
    from voltage import *
    createFile()
    from pdRate import *
    createFile()
    from summary import *
    createFile()

