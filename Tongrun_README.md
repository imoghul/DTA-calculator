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

The program must be run from the parent directory of the scripts. This means that run.bat should be in the parent directory. The script will also only need to look at SUM files

##### Directory Selection
When the program launches with test directories passed in, the stage of picking directories is skipped. If 'i' was used as the test directory then directories will have to be chosen. 

The first directory chosen will be the output directory. This is the directory in which the output "summary.csv" will be put

The second one will be the directory in which tests will be read from. It is safe to choose a parent directory as it will recursively check all sub directories

##### Parsing
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
for sub categories enter region:value
for example to get calibration glycol you type: Calibration Data:Glycol@5
to remove an element type r and the number, for example: r 1
to end press enter
input:
```
At the top is a list of the data that will be parsed out of the test files. 

The syntax is as follows: ```Region (conditional):Data Field@Column#```. The aspect to define is Region. A Region is starts in the csv file when there is a row with only the first cell having data. For example Calibration Data, Post Calibration Data, and UUT Responses are all regions. This will only be included if necessary. As for the first entry Model ID, it is not in a region therefore it should not be included. Data Field is the value that is sought. This does not have to be the first cell in the row, rather it just needs to be in the row. After the '@' comes the column number which is simply the number of the column that the data actually appears. The column numbers start at 1. 

The commands for editing are as follows. To add an entry simply type it into the input space and press enter. to remove one type: ```r #``` with # being the number to the left of the entry. and to finalize just press enter without any characters.

After this the parsing will commence, and data will be stored as specified earlier