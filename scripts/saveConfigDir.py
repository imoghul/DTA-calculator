from tkinter import *
from tkinter import filedialog
from os.path import expanduser
root = Tk()
root.withdraw()


def writeConfigDir(home):
    with open(
        # expanduser("~")+"/"
        home+"EOLT-Test-Analyzer-configdir.txt", "w"
        ) as f:
        f.write(filedialog.askdirectory(title="Choose the config directory") + "/")
