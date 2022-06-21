# EOLT Test Script

## Launch

#### Manual
```shell
python EOLT-Test-Analyzer/runTongrun.py <test directories>
# example: python EOLT-Test-Analyzer/runTongrun.py TEST\ DATA/test1 TEST\ DATA/test2
# test directory can be the letter "i" for graphical selection
``` 
#### Automatic
Double click run.bat


## Usage

The program must be run from the parent directory of the scripts. This means that run.bat should be in the parent directory

When the program launches with test directories passed in, the stage of picking directories is skipped. If 'i' was used as the test directory then directories will have to be chosen. 

The first directory chosen will be the output directory. This is the directory in which the output "summary.csv" will be put

The second one will be the directory in which tests will be read from. It is safe to choose a parent directory as it will recursively check all sub directories
