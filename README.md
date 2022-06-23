# EOLT Test Script

## Install Dependencies

* Install python 
  * windows store
* Install following module:
```shell
python -m pip install python-docx
```

## Build

The project will need to be built due to the different file structure across different systems that will use the script. 

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

The program utilizes a file called preferences.json. The syntax of this file will be explained. This file is used to determine what the script will retrieve from the tests. Another file, locations.json, must be in the same folder as the .exe file. This file may be edited if the user desires, changes will be handled by the script.


#### Directory Selection
When the program launches you will be prompted with this:
```
Press enter to use previous locations
To choose new locations enter any other character:
```
When running the first time you should manually select the directories and files. To do this type any character and press enter. This will lead to a series of windows opening asking to select directories or files. If you want to keep the default then click cancel

The first directory chosen will be the output directory. This is the directory in which the output "summary.csv" will be put

The second one will be the directory in which certificates go which will contain TEMPLATE.docx

The third one is a file selection in which you will select your preferences.json file

The fourth one will be the directory in which tests will be read from. It is safe to choose a parent directory as it will recursively check all sub directories


If manual directory Selection was not chosen then the data will automatically be stored in your previous selections

A suggested file tree is shown below:

```
EOLT
│
└───OUTPUT        
|       |summary.csv
|       └───Certificates
|           |TEMPLATE.docx
|           |*_certificate.docx   
│   
└───EOLT-Scripts
        |run.exe
        |preferences.json
        |locations.json
```

#### Parsing
Parsing is defined in a JSON file called preferences.json in the same directory as the scripts. In this file the parsing of the different types of files is specified. FT2 SUM and FT3 are currently the only ones supported and needed

```json
{
    "// Only supports FT2 SUM, and FT3 currently":"",
    
    "FT2 SUM":[
        "Model ID@2",
        "TestResult@2",
        "Calibration Data:Air1@5",
        "Calibration Data:Air2@5",
        "Calibration Data:Glycol@5",
        "Post Calibration Data:Air1@5",
        "Post Calibration Data:Air2@5",
        "Post Calibration Data:Glycol@5",
        "Calibration Data:Air@5",
        "Post Calibration Data:Air@5"
    ],

    "FT3":[
        "Barcode 8"
    ]
}
```
Above is a list of the data that will be parsed out of the test files. Different tests have different syntax due to the nature of how the csv files are layed out. The preferences for each test is a list of different elements. The syntax for a list being ```[element1, element2, element3]``` To assign this list to a test you will you the syntax ```"test":[element1, element2, element3]```. Each one of these also needs to be separated by a comma aswell.

##### Determining The Test

To determine what type of test a csv file is, the file name is observed with certain assumptions. If it contains "\_SUM" then it is FT2 SUM. Otherwise if it contains "\_RAW" it is FT2 RAW. Otherwise if it contains "FT3\_" or "ft3\_" it is FT3. Otherwise it is FT1.

##### FT2 SUM

The syntax is as follows: ```Region(conditional):Data Field@Column#```. The first aspect to define is Region. A Region starts in the csv file when there is a row with only the first cell having text. For example Calibration Data, Post Calibration Data, and UUT Responses are all regions. This will only be included if necessary. As for the first entry Model ID, it is not in a region therefore a Region should not be included. The next value to define, Data Field, is the value that is sought. This must be the first cell in the row. After the '@' comes the column number, which is simply the number of the column that the data actually appears. The column numbers start at 1. 

Due to the nature of the SUM file, being that each file corresponds to 1 unit and data is spread across rows rather than columns, the script will go row by row checking for the data it needs

##### FT3

For FT3 your list will simply contain all of the headings you want to retrieve. The script will then go through all the FT3 files and pick up the Serial Number and the data in the requested headings

##### Parsing Procedure
After this the parsing will commence, and data will be stored as specified earlier.