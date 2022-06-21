import csv
import glob
import os
import json
import sys

from click import edit
from factory import *
from tkinter import filedialog
from tkinter import *

dirs=""
outdir = ""
certdir = ""

if(sys.argv[1] == 'i'):
    root = Tk()
    root.withdraw()
    outdir = filedialog.askdirectory()+"/"
    certdir = filedialog.askdirectory()+"/"
elif(sys.argv[1] == 'd'):
    with open("EOLT-Test-Analyzer/dirs.json") as file:data=json.load(file)
    if(len(data)<3): raise Exception("\n\nInvalid saved directores. Try manually before re-attempting this method")
    outdir = data["out_dir"]
    certdir = data["certificate_dir"]
    dirs = [data["search_dirs"]]
else:
    raise Exception("\n\nUse valid arguments")

transferCertDir(certdir)

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
            raise Exception("\n\nUse valid arguments")
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
        "usage: python EOLT-Test-Analyzer/main.py <test directories>")
    exit()

createFile()



lines = {}
lines["out_dir"] = outdir+("/" if outdir[-1]!="/" and outdir[-1]!="\\" else "")
lines["certificate_dir"] = certdir+("/" if outdir[-1]!="/" and outdir[-1]!="\\" else "")
lines["search_dirs"] = ' '.join([d+("/" if d[-1]!="/" and d[-1]!="\\" else "") for d in dirs])
with open("EOLT-Test-Analyzer/dirs.json", "w") as f:
    json.dump(lines,f,indent=4)