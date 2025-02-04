# EOLT Test Script

Please read the following before attempting to use this software.

## Download 

Navigate to https://github.com/imoghul/EOLT-Test-Analyzer/releases, and download executable for latest release
Also download the ```default.zip``` file 

## Launch

Double click ```EOLT-Test-Analyzer.exe```


## Usage

### Directory Selection
The first time the program is run, it will prompt you to choose a config directory, choose the directory in which you wish to put your config files. This can be changed by editing or deleting ```configdir.txt``` in your home directory. This prompt will also appear anytime ```configdir.txt``` is destroyed.

After this, you will be prompted with this:
```
Press enter to use previous locations
To choose new locations enter any other character:
```
When running the first time you must manually select the directories and files. To do this, type any character and press enter. This will lead to a series of windows opening, asking for directories. If you have already entered directories in a previous run, or entered them [manually](#locations)  in ```locations.json``` and want to keep the default then click cancel

1. The first directory to choose will be the output directory. This is the directory in which the output summary file will be placed.

2. The second one will be the directory in which certificates go. This directory must contain ```TEMPLATE.docx``` which is the template word document for the other certificates.

3. The third one will be the directory in which tests will be read from. It is safe to choose a parent directory as it will recursively check all sub directories


If manual directory selection was not chosen (enter was pressed without any other characters), then the previous selections for the last run will be used.

### Configuration Files
#### JSON Basics

JSON is the file type used to define settings for this script, similar to how ```.xml``` and ```.INI``` files are used. A specialized text editor such as Notepad++, which should be pre-installed on Windows, is recommened for editing these files. 


In the JSON files for this script, data is stored in "dictionaries". All of the preferences are are stored in one big dictionary. The syntax for a dictionary is:
```json
{
    "key1":data1,
    "key2":data2,
    "key3":data3
}
```
Lists are used in many different instances in these json files. The syntax for a list is: ```[element1, element2, element3]```. 

All text must be surrounded by quotations marks. Inside the quotation marks the character "\\" must become "\\\\" , " " " must become " \\\" "

#### JSON In This Script

The program utilizes two configuration files that will be in the aforementioned config directory. The first one being ```locations.json```. This one does not need to be changed, though it can be. The second one is ```preferences.json```. This is where the preferences for retrieving data and other settings is stored. The syntax for these files will be discussed later.


The preferences for this script are defined in a JSON file named ```preferences.json``` in the configuration directory. In this file the parsing of the different types of files is specified. FT2 SUM, FT3, and FT1 are currently the only ones supported and needed. There are some default paramaters that are included regardless of what's in ```preferences.json```, these are:
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
                "check board type is freezer"
            ],
            "region": "UUT Responses",
            "column": 5,
            "column header": "Type Freezer"
        },
        {
            "test": "FT3",
            "title": "Barcode 8"
        },
        {
            "test": "FT1",
            "title": "StepResult",
            "step": "Verify TEC FW version"
        },
        {
            "test": "FT1",
            "title": "PCID"
        }
    ],
    "Generate Certificates": true,
    "PDF Certificates": true,
    "Avoid": [
        {
            "FT2 SUM:Model ID": [
                "TSX",
                "GA"
            ]
        },
        {
            "FT2 SUM:Model ID": [
                "PF",
                "P20"
            ],
            "Type Freezer": [
                "TRUE"
            ]
        }
    ],
    "Limit": [
        {
            "FT2 SUM:Model ID": [
                "TSX"
            ],
            "FT2 SUM:TestResult": [
                "Test Complete"
            ]
        },
        {
            "FT2 SUM:Model ID": [
                "PF"
            ]
        }
    ],
    "Dates": [
        {
            "test": "FT1",
            "Day": 3,
            "Month": 3,
            "Year": 2022
        },
        {
            "test": "FT3",
            "Year": 2021
        }
    ],
    "Master Summary File Tests":["FT1","FT2 SUM","FT3"],
}
```

##### Test Preferences

The test preferences are specifically stored in a list under the key "Test Preferences". In this list, test preferences are stored in dictionaries of their own. Each dictionary has 2 required keys and additional ones depending on test type. The 2 that are required are "test" and "title". The key "test" corresponds to the type of test file type the preference applies to. The key "title" corresponds to the name of the data field that you want to retrieve with the exact same spelling it appears in the document. Each preference also contains an optional key "hide", which determines whether or not to include it in the summary file. Another optional key is the "column header". This will be added to the column header in the summary file and should describe what the data in that header indicates. It is also used to retrieve more than 1 data field from a row. Since it is optional, the text itself will not be used to retrieve the data, instead the column number will be used. If this is not included then a column header will automatically be generated for the preference.

Different tests have different syntax and required keys due to the nature of how the corresponding csv files are layed out. The spellings for different tests are 
* FT1 - FT1 files
* FT2 SUM - FT2 summary files
* FT2 RAW - FT2 raw data files
* FT3 - FT3 files
##### Generate Certificates and PDF Certificates
The key "Generate Certificates" will either be ```false``` or ```true``` and will determine whether or not certificates should be generated. Note the lack of quotation marks, this only applies to this entry and numbers. "PDF Certificates" will convert all the certificates in the certificate directory to pdfs after generating the docx format. "Generate Certificates" must be ```true``` for pdf conversion to be able to take place.

##### Master Summary File Tests
This key contains a list with the test types to include in the master summary file.

##### Avoid and Limit

These are used in defining which values to avoid and limit to. Avoid meaning it will not include them, and Limit meaning it will only include them. Each of these are a list of dictionaries of their own. Each dictionary in these lists will contain data with the key being the header of the column and the data pertaining to that key being a list. Each key will have a list of text enclosed by quotation marks. These lists define all of the contents that must be in the key pertaining to the list. The dictionaries in each define a certain type of device to limit or avoid. Only one of these dictionaries must be fulfilled in order to be avoided or limited. The key may also be "*" in which case it will look through all of the headers instead of just one. In the above sample, all "TSX" models that don't contain "GA", and have "Test Complete" for the test result will be included. Also all devices with "PF" in the Model ID, ignoring the ones with "P20" and "TRUE" for freezer type, will be included.

If you choose to avoid or limit, be aware of the fact that certain certificates may not be generated. For example if avoid and limit weild only FT3 results then certificates will not be generated since they require FT2 SUM data. If you would like certificates for the devices, it is recommended to run again, limiting to those serial numbers

##### Dates

Dates is used to determine which dates to look at. While Avoid and Limit can also theoretically be used for this, this is an easier and more readable way of controlling which dates are included. "Dates" is a list of dictionaries each containing "test" which will determine the test type. They may also include "Year", "Monty", and "Day". Not including one implies the user is fine with it being ignored. Though this is technically possible with avoid and limit, it is discouraged as desired results may not be achieved due to zero padding of dates

#### FT2 SUM

The syntax for FT2 SUM test preferences is as follows: Each preference corresponds to a data value to extract from the test file. Each dictionary must contain keys "title", "column", "test" with optional keys  "region" and "column header". The first aspect to define is region. A region starts in the csv file when there is a row with only the first cell having text. "Calibration Data", "Post Calibration Data", and "UUT Responses" are all examples of regions. This will only be included if necessary. As for the first entry in the sample above, Model ID, it is not in a region therefore a region should not be included. The next value to define, "title", is the value that is sought. This must be the exact text in the first cell in the row. After that comes the column number, "column", which is simply the number of the column that the data actually appears in. The column numbers start at 1. 

#### FT3

For FT3 your preference will simply contain the heading/column you want to retrieve under the key "title", along with the test file type under the key "test".

#### FT1

In an FT1 csv output file, there are 2 types of data. The data in the beginning of the file, and the data in the table below it. Hence, there are 2 ways of defining an FT1 preference. They key "step" defines which "Step name" to look at in the FT1 test file while "title" will be the name of the column to look at. If a step is not in one or more of the test files the way it is in the preferences file, then the data will not make it to the final summary file. If a step is not defined in a preference, though it should be according to the layout of the test file, then the script will never find that data and will end up being ignored. If the "step" key is not included and is not needed, this would entail it is a preference from the upper portion of the FT1 test file. In this case, "title" should be the text in the first column and the script will retrieve whatever is in the second column.

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

* Under the key "out_dir", the directory for the output summary file is stored
* Under the key "certificate_dir" is where the directory with the ```TEMPLATE.docx``` and the other output certificates is stored. 
* Under the key "search_dirs" is a list of directories. These are the directories that will be searched recursively for test files to read. If using the graphical selection in the runtime of the script, only one directory can be selected. If one wishes to select more than one, they must resort to adding them here.

These values are overwritten when they are selected from the script

## Runtime

### Determining The Test

To determine what type of test a csv file is, the file name is observed with certain assumptions. If it contains "\_SUM" then it is FT2 SUM. Otherwise if it contains "\_RAW" it is FT2 RAW. Otherwise if it contains "FT3\_" or "ft3\_" it is FT3. Otherwise, if cell A1 of the test file is "Model ID" or "Traveller ID", it is FT1.
### Execution
After reading ```preferences.json``` and ```locations.json``` the parsing will commence, and data will be stored at the output folder in the summary file. Note that this script uses replace mode instead of append mode, meaning that the summary file will be overwritten every time, rather than added to. It is important to make sure that none of the "Test Preferences" config entries have duplicate headers. This will cause the script to overwrite data on the last one it sees. This should only be used if it is known that a certain the config entries won't all appear in the same files. For example, Post Calibration Air2 (for larger units) and Post Calibratoin Air (for tote units) won't appear in the same file, therefore putting them under the same header won't cause any overwriting to occur
### Errors
Errors that take place during runtime will be recorded in ```errors.log``` in the output directory. Errors that occur before an output directory can be determined will appear on the script's output

****

An extra script with the name ```EOLT-Test-Analyzer-FT2_RAW.exe``` is provided with no support/documentation. This is an old script that was included due to the benefit it may contribute. It will use the same folders that the main script uses, but does not utilize a config file as it is just used to retrive all the data possible from FT2 RAW files. Output will be stored in ```comprehensive_summary.csv```

****

For updates check: https://github.com/imoghul/EOLT-Test-Analyzer/tree/main