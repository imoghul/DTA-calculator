from tkinter import *
from tkinter import filedialog
root = Tk()
root.withdraw()
with open("configdir.txt","w") as f:f.write(filedialog.askdirectory(title="Choose the config directory")+"/") 