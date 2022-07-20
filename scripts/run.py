import csv
import glob
import os
import json
from os.path import expanduser
import sys

sys.tracebacklimit = -1
from eolt import *
from tkinter import filedialog
from tkinter import *


home = expanduser("~")+"/"

try:
    with open(home+"configdir.txt") as f:
        configdir = f.read()
except:
    from saveConfigDir import writeConfigDir
    writeConfigDir()
    with open(home+"configdir.txt") as f:
        configdir = f.read()


# try:
#     try:
#         basePath = sys._MEIPASS
#     except Exception:
#         basePath = os.path.abspath(".")
#     bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
#     configtxt = os.path.join(bundle_dir, "configdir.txt")

#     with open(configtxt, "r") as f:
#         configdir = f.read()
# except:
#     raise Exception("Error reading config directory try re-building")

cli = False
mode = (
    (
        "d"
        if input(
            "Press enter to use previous locations\nTo choose new locations enter any other character: "
        )
        == ""
        else "i"
    )
    if not cli
    else sys.argv[1]
)
print()
dirs = ""
outdir = ""
certdir = ""


preferencesFile = configdir + "/preferences.json"
locationFile = configdir + "/locations.json"

if cli and len(sys.argv) < 2:
    raise Exception("usage: python run.py <test locations>")

if mode == "d":
    try:
        with open(locationFile) as file:
            data = json.load(file)
        outdir = data["out_dir"]
        certdir = data["certificate_dir"]
        dirs = data["search_dirs"]
        if type(dirs) != list:
            dirs = [dirs]
    except:
        raise Exception(
            "One or more of the directories couldn't be found, please select locations manually"
        )
elif mode == "i":
    root = Tk()
    root.withdraw()
    outdir = filedialog.askdirectory(title="Select the output directory") + "/"
    certdir = filedialog.askdirectory(title="Select the certificate directory") + "/"
    # preferencesFile = filedialog.askopenfilename(title = "Select the preferences file")
    try:
        with open(locationFile) as file:
            data = json.load(file)
        _outdir = data["out_dir"]
        _certdir = data["certificate_dir"]
        _dirs = data["search_dirs"]
        if type(_dirs) != list:
            _dirs = [_dirs]
    except:
        raise Exception(
            "One or more of the directories couldn't be found, please select ALL locations manually"
        )
    if outdir == "/":
        outdir = _outdir
    if certdir == "/":
        certdir = _certdir

transferDirs(certdir, preferencesFile, outdir)


def createFile(sumType):
    global dirs
    with open(
        outdir + outFileName + "_" + "_".join(sumType) + ".csv", mode="w", newline=""
    ) as out:
        writer = csv.writer(out)
        # output header to csv
        writeHeaderToFile(writer)
        # get list of directories to run

        if mode == "i":
            root = Tk()
            root.withdraw()
            dirs = [
                filedialog.askdirectory(title="Select the input tests directory") + "/"
            ]
            if dirs[0] == "/":
                dirs = _dirs
        elif cli and mode != "d":
            dirs = sys.argv[1:]
        elif not cli and mode != "d":
            raise Exception("\n\nUse valid arguments")

        original = os.getcwd()

        for dir in dirs:
            print(
                "Gathering File Names From The %s Directory..."
                % ordinal(dirs.index(dir) + 1)
            )
            fileNames = glob.glob(dir + globType, recursive=True)
            # runs for every directory
            writeDataToFile(writer, dir, [f.replace("\\", "/") for f in fileNames])
        try:
            writeSummaryToFile(writer)
        except:
            raise Exception("Couldn't write summary file")


try:
    with open(preferencesFile) as f:
        retrieveData = json.load(f)
    moveToBeginning(retrieveData["Master Summary File Tests"], "FT")
    moveToBeginning(retrieveData["Master Summary File Tests"], "FT2 RAW")
    moveToBeginning(retrieveData["Master Summary File Tests"], "FT2 SUM")
    moveToBeginning(retrieveData["Master Summary File Tests"], "FT1")
    createFile(retrieveData["Master Summary File Tests"])

except (PermissionError):
    raise Exception("Output file couldn't be opened. Close the file if it is open")
except Exception as e:
    raise e

lines = {}
lines["out_dir"] = outdir + ("/" if outdir[-1] != "/" and outdir[-1] != "\\" else "")
lines["certificate_dir"] = certdir + (
    "/" if outdir[-1] != "/" and outdir[-1] != "\\" else ""
)
lines["search_dirs"] = [
    d + ("/" if d[-1] != "/" and d[-1] != "\\" else "") for d in dirs
]

try:
    with open(locationFile, "w") as f:
        json.dump(lines, f, indent=4)
except (PermissionError):
    raise Exception("Locations file couldn't be opened. Close the file if it is open")
except Exception as e:
    raise e

os.system("pause")
