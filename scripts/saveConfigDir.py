from tkinter import *
from tkinter import filedialog
from os.path import expanduser
root = Tk()
root.withdraw()

# saves the configdir in the config dir text file after asking the user for it
def writeConfigDir(home):
    with open(
        # expanduser("~")+"/"
        home+"EOLT-Test-Analyzer-configdir.txt", "w"
        ) as f:
        f.write(filedialog.askdirectory(title="Choose the config directory") + "/")
