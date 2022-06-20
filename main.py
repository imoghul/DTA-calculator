import csv
import glob
import os
import sys
from tkinter import filedialog
from tkinter import *



def createFile():
    with open("CSV OUTPUT/"+outFileName, mode="w", newline='') as out:
        writer = csv.writer(out)
        # output header to csv
        writeHeaderToFile(writer)
        # get list of directories to run
        if len(sys.argv) > 2:
            if(sys.argv[2] == 'i'):
                root = Tk()
                root.withdraw()
                dirs = [filedialog.askdirectory()]#.replace("/","\\")

            else: dirs = sys.argv[2:]
        else:
            dirs = [os.getcwd()+"/TEST DATA/"]
        # dirs.insert(0, "baseline")
        # print(dirs)
        original = os.getcwd()

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
elif (sys.argv[1] == "t"):
    from tongrun import *
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
    from tongrun import *
    createFile()

