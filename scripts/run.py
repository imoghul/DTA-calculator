from copyreg import pickle
import csv
import glob
import os
import json
import sys

from eolt import *
from tkinter import filedialog
from tkinter import *

try:
    basePath = sys._MEIPASS
except Exception:
    basePath = os.path.abspath(".")
bundle_dir = getattr(
    sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
configtxt = os.path.join(bundle_dir, 'configdir.txt')

cli = False
mode = ('d' if input("Press enter to use previous locations\nTo choose new locations enter any other character: ")
        == "" else 'i') if not cli else sys.argv[1]

dirs = ""
outdir = ""
certdir = ""

with open(configtxt, "r") as f:
    configdir = f.read()

preferencesFile = configdir+"\\preferences.json"
locationFile = configdir+"\\locations.json"

if (cli and len(sys.argv) < 2):
    raise Exception(
        "usage: python EOLT-Test-Analyzer/main.py <test locations>")

if(mode == 'd'):
    try:
        with open(locationFile) as file:
            data = json.load(file)
        outdir = data["out_dir"]
        certdir = data["certificate_dir"]
        dirs = data["search_dirs"]
        if(type(dirs) != list):
            dirs = [dirs]
    except:
        raise Exception(
            "\n\nOne or more of the directories couldn't be found, please select locations manually")
elif(mode == 'i'):
    root = Tk()
    root.withdraw()
    outdir = filedialog.askdirectory(title="Select the output directory")+"/"
    certdir = filedialog.askdirectory(
        title="Select the certificate directory")+"/"
    # preferencesFile = filedialog.askopenfilename(title = "Select the preferences file")
    try:
        with open(locationFile) as file:
            data = json.load(file)
        _outdir = data["out_dir"]
        _certdir = data["certificate_dir"]
        _dirs = data["search_dirs"]
        if(type(_dirs) != list):
            _dirs = [_dirs]
    except:
        raise Exception(
            "\n\nOne or more of the directories couldn't be found, please select ALL locations manually")
    if(outdir == "/"):
        outdir = _outdir
    if(certdir == "/"):
        certdir = _certdir
    # if(preferencesFile==""): preferencesFile = _preferencesFile
    # print(outdir,certdir,preferencesFile)

# print(outdir, certdir, preferencesFile)

transferDirs(certdir, preferencesFile)


def createFile():
    global dirs
    with open(outdir+outFileName, mode="w", newline='') as out:
        writer = csv.writer(out)
        # output header to csv
        writeHeaderToFile(writer)
        # get list of directories to run

        # if cli and len(sys.argv) < 2:
        if(mode == 'i'):
            root = Tk()
            root.withdraw()
            dirs = [filedialog.askdirectory(
                title="Select the input tests directory")+"/"]
            if dirs[0] == "/":
                dirs = _dirs
        elif(cli and mode != 'd'):
            dirs = sys.argv[1:]
        elif(not cli and mode != 'd'):
            raise Exception("\n\nUse valid arguments")

        # print(dirs)
        original = os.getcwd()

        for dir in dirs:
            # try:os.chdir(dir)
            # except: raise Exception(f"Invalid directory: {dir}")
            fileNames = glob.glob(dir+globType, recursive=True)
            # runs for every directory
            writeDataToFile(
                writer, dir, [f.replace("\\", "/") for f in fileNames])
            # os.chdir(original)  # return to original dir

        writeSummaryToFile(writer)


createFile()

lines = {}
lines["out_dir"] = outdir + \
    ("/" if outdir[-1] != "/" and outdir[-1] != "\\" else "")
# lines["preferences_file"] = preferencesFile
lines["certificate_dir"] = certdir + \
    ("/" if outdir[-1] != "/" and outdir[-1] != "\\" else "")
lines["search_dirs"] = [
    d+("/" if d[-1] != "/" and d[-1] != "\\" else "") for d in dirs]


with open(locationFile, "w") as f:
    json.dump(lines, f, indent=4)

# with open(locationFile) as f:
#     print(json.load(f))

os.system("pause")
