import csv, glob, os, sys
from numpy import mean
from calibration import *

def createFile():
  with open(outFileName, mode="w", newline='') as out:
      writer = csv.writer(out)
      #output header to csv
      writeHeaderToFile(writer)
      # get list of directories to run
      if len(sys.argv) > 2:
          dirs = sys.argv[2:]
      else:
          dirs = [os.getcwd()]
      dirs.insert(0, "baseline")
      original = os.getcwd()

      for dir in dirs:
          os.chdir(dir)
          fileNames = glob.glob(globType, recursive=True)
          fileNames.sort()
          writeDataToFile(writer, dir, fileNames)  # runs for every directory
          os.chdir(original)  # return to original dir

      writeSummaryToFile(writer)


if(len(sys.argv)<2):
  print("enter arguments: d/c/b folders")
  exit()
elif(sys.argv[1]=="d"):
  from dta import *
  createFile()
elif(sys.argv[1]=="c"):
  from calibration import *
  createFile()
else:
  from calibration import *
  createFile()
  from dta import *
  createFile()




