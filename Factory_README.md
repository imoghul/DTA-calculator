# EOLT Test Script

## Install Dependencies

* Install python 
  * windows store
* Install following module:
```shell
python -m pip install python-docx
```

## Launch

#### Command Line
```shell
python EOLT-Test-Analyzer/runFactory.py <test directories>
# example: python runFactory.py TEST\ DATA/test1 TEST\ DATA/test2
# test directory can be the letter "i" for graphical selection
# the letter "d" will use the directories from the last run 
``` 
#### Automatic
Double click executable


## Usage

The program utilizes a file called preferences.json. The syntax of this file will be explained. This file is used to determine where 


#### Directory Selection
When the program launches you will be prompted with this:
```
Press enter to use previous locations
To choose new locations enter any other character:
```
When running the first time you should manually select the directories and files. To do this type any character and press enter. This will lead to a series of windows opening asking to select directories or files. If you want to keep the default then click cancel

The first directory chosen will be the output directory. This is the directory in which the output "summary.csv" will be put

The second one will be the directory in which tests will be read from. It is safe to choose a parent directory as it will recursively check all sub directories

The third one will be the directory in which certificates go which will contain TEMPLATE.docx

If manual directory Selection was not chosen then the data will automatically be stored in FACTORY in the following suggested directory tree

```
EOLT SCRIPTS
│   run.bat    
│
└───OUTPUT
│   │   └───FACTORY
|   |   |   summary.csv
|   |   |   └───Certificates
|   |   |   |   TEMPLATE.docx
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
Parsing is defined in a text file called preferences.txt in the same directory as the scripts

```
0: Model ID@2
1: Calibration Data:Air1@5
2: Calibration Data:Air2@5
3: Calibration Data:Glycol@5
4: Post Calibration Data:Air1@5
5: Post Calibration Data:Air2@5
6: Post Calibration Data:Glycol@5
```
At the top is a list of the data that will be parsed out of the test files. 

The syntax is as follows: ```Region(conditional):Data Field@Column#```. The first aspect to define is Region. A Region starts in the csv file when there is a row with only the first cell having text. For example Calibration Data, Post Calibration Data, and UUT Responses are all regions. This will only be included if necessary. As for the first entry Model ID, it is not in a region therefore a Region should not be included. The next value to define, Data Field, is the value that is sought. This must be the first cell in the row. After the '@' comes the column number, which is simply the number of the column that the data actually appears. The column numbers start at 1. 

After this the parsing will commence, and data will be stored as specified earlier