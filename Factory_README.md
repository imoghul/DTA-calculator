# EOLT Test Script

## Install Dependencies

* Install python (windows store)
* Install following modules:
```shell
python -m pip install python-docx
python -m pip install numpy
```

## Launch

#### Manual
```shell
python EOLT-Test-Analyzer/runFactory.py <test directories>
# example: python EOLT-Test-Analyzer/runFactory.py TEST\ DATA/test1 TEST\ DATA/test2
# test directory can be the letter "i" for graphical selection
# the letter "d" will use the directories from the last run 
``` 
#### Automatic
Double click run.bat


## Usage

The program must be run from the parent directory of the scripts. This means that run.bat should be in the parent directory. 

#### Directory Selection
When the program launches with test directories passed in, the stage of picking directories is skipped. If 'i' was used as the test directory then directories will have to be chosen. If 'd' was used the program will use the directores chosen in the last run. If this gets corrupted then try manually, this should fix it.

The first directory chosen will be the output directory. This is the directory in which the output "summary.csv" will be put

The second one will be the directory in which tests will be read from. It is safe to choose a parent directory as it will recursively check all sub directories

If manual directory Selection was not chosen then the data will automatically be stored in FACTORY in the following suggested directory tree

```
EOLT SCRIPTS
│   run.bat    
│
└───OUTPUT
│   │   └───FACTORY
|   |   |   summary.csv
|   |   |   └───Certificates
|   |   |   |   *.docx
|   
│   
└───EOLT-Test-Analyzer
    │   runFactory.py
    │   factory.py
    |   utils.py
    |   certificate.py
```

#### Parsing
Once directories have been chosen, the parsing can be edited. You will see a screen similar to this:

```
0: Model ID@2
1: Calibration Data:Air1@5
2: Calibration Data:Air2@5
3: Calibration Data:Glycol@5
4: Post Calibration Data:Air1@5
5: Post Calibration Data:Air2@5
6: Post Calibration Data:Glycol@5

to add an element type the exact name and column number separated by an @
for sub categories enter region:value@column#
for example to get calibration glycol you type: Calibration Data:Glycol@5
to remove an element type r and the number, for example: r 1
to end press enter
input:
```
At the top is a list of the data that will be parsed out of the test files. 

The syntax is as follows: ```Region(conditional):Data Field@Column#```. The first aspect to define is Region. A Region starts in the csv file when there is a row with only the first cell having text. For example Calibration Data, Post Calibration Data, and UUT Responses are all regions. This will only be included if necessary. As for the first entry Model ID, it is not in a region therefore a Region should not be included. The next value to define, Data Field, is the value that is sought. This must be the first cell in the row. After the '@' comes the column number, which is simply the number of the column that the data actually appears. The column numbers start at 1. 

The commands for editing are as follows. To add an entry simply type it into the input space. to remove one type: ```r #``` with # being the number to the left of the entry. To finalize just press enter without any characters.

After this the parsing will commence, and data will be stored as specified earlier