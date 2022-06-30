# EOLT Test Script

Please read the following before attempting to use this software.

## Download Source Code

1. Press: https://github.com/imoghul/EOLT-Test-Analyzer/archive/refs/heads/main.zip
2. Extract Contents

## Install Dependencies
### Manually
* Install python (last tested on version 3.10.5)
  * Windows Store (recommended)
  * https://www.python.org/downloads/
* Simultaneously press Win+R
* Type cmd and press enter
* Install following modules by pasting into the command line:
```shell
python -m pip install docx==0.2.4 docx2pdf==0.1.8 python_dateutil==2.8.2 python_docx==0.8.11
```
### Automatically
Double click on ```setup.bat```.
## Build

The project will need to be built due to the different file structure across different systems that will use the script. Building is not necessary if using the command line. To build the script double click on ```build.dat```, or ```build.sh``` if using a Mac or Linux machine. You will be prompted to pick the config folder. NOTE: You will not be able to change this later on without rebuilding. Choose a folder in which you wish to put configuration files. 

Once finished building, you should find a file named ```run.exe```. This file will be the executable that will be used to run the script. The only other files needed are the contents of the ```default``` directory. Apart from that, all other files can be deleted.

## Launch

### Command Line
If you would like to use the script without building you can do so by running it through the command line. First navigate to the directory with the script files in the terminal. Before being able to run the script you will need to execute a different script that will prompt you to pick a config folder. The config folder will be stored in ```configdir.txt``` which must stay in the same directory as the rest of the scripts. The contents of ```configdir.txt``` can be changed later on by running the same script or manually editing the file. 

*Command to save configuration directory*
```shell
python saveConfigDir.py
```


From this point on to run the script, simply enter the following into the command line. 

*Command to run the script*
```shell
python run.py
``` 

Keep in mind that these steps are unnessary if you choose to use the executable generated during the build

### Executable
Double click ```run.exe``` generated by the build script


## Usage

### Directory Selection
When the program launches you will be prompted with this:
```
Press enter to use previous locations
To choose new locations enter any other character:
```
When running the first time you must manually select the directories and files. To do this, type any character and press enter. This will lead to a series of windows opening, asking for directories. If you have already entered directories in a previous run, or entered them [manually](#locations)  in ```locations.json``` and want to keep the default then click cancel

1. The first directory to choose will be the output directory. This is the directory in which the output "summary.csv" will be placed.

2. The second one will be the directory in which certificates go. This directory must contain ```TEMPLATE.docx``` which is the template word document for the other certificates.

3. The third one will be the directory in which tests will be read from. It is safe to choose a parent directory as it will recursively check all sub directories


If manual directory selection was not chosen (enter was pressed without any other characters), then the previous selections for the last run will be used.

### Configuration Files
#### JSON Basics

JSON is the file type used to define settings for this script, similar to how ```.xml``` and ```.INI``` files are used.


In the JSON files for this script, data is stored in "dictionaries". All of the preferences are are stored in one big dictionary. The syntax for a dictionary is:
```json
{
    "key1":data1,
    "key2":data2,
    "key3":data3
}
```
Lists are used in many different instances in these json files. The syntax for a list is: ```[element1, element2, element3]```. 

All text must be surrounded by quotations marks. Inside the quotation marks the character "\\" must become "\\\\" 

#### JSON In This Script

The program utilizes two configuration files that will be in the aforementioned config directory. The first one being ```locations.json```. This one does not need to be changed, though it can be. The second one is ```preferences.json```. This is where the preferences for retrieving data and other settings is stored. The syntax for these files will be discussed later.


The preferences for this script are defined in a JSON file named ```preferences.json``` in the configuration directory. In this file the parsing of the different types of files is specified. FT2 SUM and FT3 are currently the only ones supported and needed. There are some default paramaters that are included regardless of what's in ```preferences.json```, these are:
* Serial Number
* Date
* File Name:FT2 SUM
* File Name:FT3

A sample ```preferences.json``` is shown below, please refer to this for syntax, spelling, and capitalization
```json
{
    "Test Preferences": [
        {
            "test": "FT2 SUM",
            "title": "Model ID",
            "column": 2
        },
        {
            "test": "FT2 SUM",
            "title": "Glycol",
            "region": "Calibration Data",
            "column": 5,
            "hide": true,
            "column header": "Calib:Glycol"
        },
        {
            "test": "FT2 SUM",
            "title": [
                "PrePullDown UUT Responses",
                "type freezer"
            ],
            "region": "UUT Responses",
            "column": 5,
            "column header": "Type Freezer"
        },
        {
            "test": "FT3",
            "title": "Barcode 8"
        }
    ],
    "Generate Certificates": true,
    "PDF Certificates": true,
    "Limit": {
        "Serial Number":["TR156","VL212"],
        "TestResult":["Test Complete"]
    },
    "Avoid": {
        "Model ID":["TSX","PF"]
    },
    "Dates": [
        {
            "Day":3,
            "Month":3,
            "Year":2022
        },
        {
            "Year":2021
        }
    ]
}
```

##### Test Preferences

The test preferences are specifically stored in a list under the key "Test Preferences". In this list, test preferences are stored in dictionaries of their own. Each dictionary has 2 required keys and additional ones depending on test type. The 2 that are required are "test" and "title". The key "test" corresponds to the type of test file type the preference applies to. The key "title" corresponds to the name of the data field that you want to retrieve with the exact same spelling it appears in the document. Each preference also contains an optional key "hide", which determines whether or not to include it in the summary file.

Different tests have different syntax and required keys due to the nature of how the corresponding csv files are layed out. The spellings for different tests are 
* FT1 - ft1 files
* FT2 SUM - ft2 summary files
* FT2 RAW - ft2 raw data files
* FT3 - ft3 files
##### Generate Certificates
The key "Generate Certificates" will either be ```false``` or ```true``` and will determine whether or not certificates should be generated. Note the lack of quotation marks, this only applies to this entry and the column entery for Test Preferences.

##### Avoid and Limit

These are used in defining which values to avoid and limit to. Avoid meaning it will not include them, and Limit meaning it will only include them. Each of these are a dictionary of their own and will contain elements with the key being the header of the row and the data pertaining to that key being a list. In the list, exact values are not necessary, rather they only must be part the data. For example, TSX is part of Model ID TSX505GA and TSX505SA, therefore both of these Model ID's will count under TSX. In the sample configuration. Only passing devices that contain TR156 or VL212 in the serial number and don't contain TSX, or PF in the Model ID will count. Essentially, this is all non TSX and PF models with passing results and TR156 or VL212 in the serial number. 

##### Dates

Dates is used to determine which dates to look at. While Avoid and Limit can also theoretically be used for this, this is an easier and more readable way of controlling which dates are included.

#### FT2 SUM

The syntax for FT2 SUM test preferences is as follows: Each preference corresponds to a data value to extract from the test file. Each dictionary must contain keys "title", "column", "test" with optional keys  "region" and "column header". The first aspect to define is region. A region starts in the csv file when there is a row with only the first cell having text. "Calibration Data", "Post Calibration Data", and "UUT Responses" are all examples of regions. This will only be included if necessary. As for the first entry in the sample above, Model ID, it is not in a region therefore a region should not be included. The next value to define, "title", is the value that is sought. This must be the exact text in the first cell in the row. After that comes the column number, "column", which is simply the number of the column that the data actually appears in. The column numbers start at 1. An optional key is the "column header". This will be added to the column header in the summary file and should describe what the data in that header indicates. It is also used to retrieve more than 1 data field from a row. Since it is optional, the text itself will not be used to retrieve the data, instead the column number will be used.

#### FT3

For FT3 your preference will simply contain the heading/column you want to retrieve under the key "title", along with the test file type under the key "test".

#### Locations
Information about which directories to use are stored in ```locations.json``` in the config directory. The syntax for this file is included in this documentation for completion and added functionality but it need not be touched if the user does not wish to.


The default ```locations.json``` provided is shown below
```json
{
    "out_dir": "",
    "certificate_dir": "",
    "search_dirs": [
        ""
    ]
}
```

* Under the key "out_dir", the directory for the output ```summary.csv``` is stored
* Under the key "certificate_dir" is where the directory with the ```TEMPLATE.docx``` and the other output certificates is stored. 
* Under the key "search_dirs" is a list of directories. These are the directories that will be searched recursively for test files to read. If using the graphical selection in the runtime of the script, only one directory can be selected. If one wishes to select more than one, they must resort to adding them here.

These values are overwritten when they are selected from the script

## Runtime

### Determining The Test

To determine what type of test a csv file is, the file name is observed with certain assumptions. If it contains "\_SUM" then it is FT2 SUM. Otherwise if it contains "\_RAW" it is FT2 RAW. Otherwise if it contains "FT3\_" or "ft3\_" it is FT3. Otherwise it is FT1.
### Execution
After reading ```preferences.json``` and ```locations.json``` the parsing will commence, and data will be stored at the output folder in ```summary.csv```. Note that this script uses replace mode instead of append mode, meaning that the ```summary.csv``` file will be overwritten every time. If the script comes across the same serial number more the once in the tests, it will take the last one, sorted by time. If there is a conflict between data in any of the files FT2 SUM takes preference.

### Remarks on Excel Master Files

There are 2 provided excel files in the defaults directory. EOLT_1 allows the user to change the summary csv file to use, while EOLT_2 requires that it be named ```summary.csv``` and be in the same directory as the EOLT_2.xlsx file. EOLT_1 does some to be buggy due to the fact that opening it for the first time on a computer with a different pathing will cause the formulas to fail. If one has the time to fix this, EOLT_1 becomes more useful. Otherwise EOLT_2 is much more stable

****
For updates check: https://github.com/imoghul/EOLT-Test-Analyzer/tree/main