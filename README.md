# Data Analyzer for Phononic Raw Data Files

## Usage

```shell
python EOLT-Test-Analyzer/main.py [d/c/v/p/s] <test directories>
# example: python EOLT-Test-Analyzer/main.py d TEST\ DATA/test1 TEST\ DATA/test2
# test directory can be the letter "i" for graphical selection
``` 

## Overview

The program will read files from a directory in the parent directory of the directory with the scripts called TEST DATA. They will be placed in a directory in the parent directory called CSV OUTPUT. The program should be run from the parent directory


## Options

* dta/d - calculates delta temperature time array
* calibration/c - extracts calibration values
* voltage/v - extracts voltages
* pulldown rate/p - caluclates the pulldown rate
* summary/s - creates a summary based on all the tests
* tongrun/t - creates a summary based off tongrun request
