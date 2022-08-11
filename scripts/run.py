import csv
import glob
import os
import json
from os.path import expanduser
import sys
import logging
# sys.tracebacklimit = -1
from tkinter import filedialog
from tkinter import *
import atexit
from eolt import *

# define exit function


def pause():
    os.system("pause")


# assign exit function to execute on exit
atexit.register(pause)

# home var defines where the config dir text file will be stored
home = ""
# use the bottom as home to store config dir at the home directory
# expanduser("~")+"/"

try:
    # if configdir text file exists, simply read the file
    with open(home+"EOLT-Test-Analyzer-configdir.txt") as f:
        configdir = f.read()
except:
    # if it doesn't exist create the file and then read it
    from saveConfigDir import writeConfigDir
    # this will create the configdir text file and store the dir based on what the user chooses
    writeConfigDir(home)
    with open(home+"EOLT-Test-Analyzer-configdir.txt") as f:
        configdir = f.read()

# defines if the file should be run through command line or not
# in cli mode, directories can be inputted as arguments into the command used to run the script
cli = False
# mode "d" is when the user doesn't select directory
# mode "i" is when the user selects a directory
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
dirs = ""  # dirs is the list of input directories
outdir = ""  # outdir is the output directory
certdir = ""  # certdir is the certificate directory

# preferencesFile is the path to the preferences.json file
preferencesFile = configdir + "/preferences.json"
# locationFile is the path to the locations.json file
locationFile = configdir + "/locations.json"

# if you are in cli mode and no directories were inputted as arguments, then ask for them
if cli and len(sys.argv) < 2:
    raise Exception("usage: python run.py <test locations>")

if mode == "d":
    try:
        with open(locationFile) as file:
            data = json.load(file)  # read the locations.json file
        outdir = data["out_dir"] # retrieve outdir
        certdir = data["certificate_dir"]  # retrieve certdir
        dirs = data["search_dirs"]  # retrieve dirs
        if type(dirs) != list:
            # if dirs is saved as a string, then convert it to a list
            dirs = [dirs]
    except:  # error handling
        raise Exception(
            "One or more of the directories couldn't be found, please select locations manually"
        )
elif mode == "i":
    root = Tk()  # construct tkinter
    root.withdraw()  # withdraw initialized window
    outdir = filedialog.askdirectory(
        title="Select the output directory") + "/"  # ask for outdir
    certdir = filedialog.askdirectory(
        title="Select the certificate directory") + "/"  # ask for certdir
    try:
        # retrieve what is already in locations.json
        with open(locationFile) as file:
            data = json.load(file)
        _outdir = data["out_dir"]
        _certdir = data["certificate_dir"]
        _dirs = data["search_dirs"]
        if type(_dirs) != list:
            _dirs = [_dirs]
    except:  # error handling
        raise Exception(
            "One or more of the directories couldn't be found, please select ALL locations manually"
        )
    if outdir == "/":  # if ESC or Cancel was pressed on tkinter prompt, then use what was already in locations.json
        outdir = _outdir
    if certdir == "/":  # if ESC or Cancel was pressed on tkinter prompt, then use what was already in locations.json
        certdir = _certdir

outdir = outdir + \
            ("/" if outdir[-1] != "/" and outdir[-1] !=
             "\\" else "") if outdir != "" else ""
certdir = certdir + (
            ("/" if certdir[-1] != "/" and certdir[-1]
             != "\\" else "") if certdir != "" else ""
        )
for i,v in enumerate(dirs):
            dirs[i] += (
            ("/" if dirs[i][-1] != "/" and dirs[i][-1]
             != "\\" else "") if dirs[i] != "" else "")

try:
    # create error logger
    logging.basicConfig(filename=outdir+"errors.log", level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)
except:  # if outdir is invalid and an errors.log can't be created, then ask them to choose everything manually again
    raise Exception(
        "One or more directories are invalid, please choose again manually")

init(certdir, preferencesFile, outdir, logger)


def createFile():
    global dirs
    with open(
        outdir + getOutFileName(), mode="w", newline=""
    ) as out:  # open the summary.csv file
        writer = csv.writer(out)
        # output header to csv
        writeHeaderToFile(writer)
        # get list of directories to run
        if mode == "i":
            root = Tk()
            root.withdraw()
            # only asks for 1 directory
            # TODO: ask for multiple directories until a Cancel or ESC
            dirs = [
                filedialog.askdirectory(
                    title="Select the input tests directory") + "/"
            ]  # ask for dirs
            if dirs[0] == "/":  # if nothing was selected then use the default
                dirs = _dirs
        elif cli and mode != "d":
            dirs = sys.argv[1:]  # if cli was
        elif not cli and mode != "d":  # if cli is False and mode is somehow not "d", an impossibility has occured, would need to change to clie = True
            raise Exception("\n\nUse valid arguments")

        locs = {}  # create output locations to overwrite locations.json
        locs["out_dir"] = outdir + \
            ("/" if outdir[-1] != "/" and outdir[-1] !=
             "\\" else "") if outdir != "" else ""  # add a "/" to the end of outdir if it doesn't already have one
        locs["certificate_dir"] = certdir + (
            # add a "/" to the end of certdir if it doesn't already have one
            ("/" if certdir[-1] != "/" and certdir[-1]
             != "\\" else "") if certdir != "" else ""
        )
        locs["search_dirs"] = [
            d + ((("/" if d[-1] != "/" and d[-1] != "\\" else "") if d != "" else "")) for d in dirs
        ]  # add a "/" to the end of every dir if it doesn't already have one

        try:
            with open(locationFile, "w") as f:
                json.dump(locs, f, indent=4)  # write to locations.json
        except (PermissionError):  # error handling
            logger.error(
                Exception("Locations file couldn't be opened. Close the file if it is open"))
        except Exception as e:  # error handling
            logger.error(e)

        for dir in dirs:  # start iterating over all the serch directories
            print(
                "Gathering File Names From The %s Directory..."
                % ordinal(dirs.index(dir) + 1)
            )  # print a messange letting the user know that the script is doing something since, I can't iterate through and make a progess bar for glob.glob
            fileNames = glob.glob(dir + globType, recursive=True)
            # runs for every directory
            writeDataToFile(
                writer, dir, [f.replace("\\", "/") for f in fileNames])
        try:
            # runs at the end of searching
            writeSummaryToFile(writer)
        except Exception as e:  # error handling
            logger.error(e)#(Exception("Couldn't write summary file"))


try:
    # run the entire procedure
    createFile()
except (PermissionError):  # error handling (file open)
    logger.error(
        Exception("Output file couldn't be opened. Close the file if it is open"))
except Exception as e:  # error handling
    logger.error(e)
