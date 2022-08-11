import csv
from datetime import datetime
import json
import glob
import os
import time
import sys
from tkinter import E
from utils import *
import random
import string
from certificate import *
import threading
import re
from tqdm import tqdm
import dateutil.parser
import logging

outFileName = "summary.csv" # tentative name for the ouptut file, should change based on "Master Summary File Tests"
globType = "**/*.csv" # chooses what types of files to read, will read in all directories for all csv files

preferencesFile = None # path for preferences.json
outdir = None # path for output directory
noDataStr = " " # the string to fill in the summary file when data isn't found. DO NOT use an empty str("") this will mess with Avoid and Limit
logger = logging.getLogger(__name__) # tentative logger before init

# generate random keys for certificate stuff, possibly a better approach
daqTempKey = "".join(
    random.choice(string.ascii_lowercase +
                  string.digits + string.ascii_uppercase)
    for i in range(20)
)
calibKey = daqTempKey
while calibKey == daqTempKey:
    calibKey = "".join(
        random.choice(string.ascii_lowercase +
                      string.digits + string.ascii_uppercase)
        for i in range(20)
    )
testResKey = calibKey
while testResKey == calibKey:
    testResKey = "".join(
        random.choice(string.ascii_lowercase +
                      string.digits + string.ascii_uppercase)
        for i in range(20)
    )
postCalibKey = daqTempKey
while postCalibKey == daqTempKey:
    postCalibKey = "".join(
        random.choice(string.ascii_lowercase +
                      string.digits + string.ascii_uppercase)
        for i in range(20)
    )
postDaqTempKey = calibKey
while postDaqTempKey == calibKey:
    postDaqTempKey = "".join(
        random.choice(string.ascii_lowercase +
                      string.digits + string.ascii_uppercase)
        for i in range(20)
    )
postCalibGlycolKey = postDaqTempKey
while postCalibGlycolKey == postDaqTempKey:
    postCalibGlycolKey = "".join(
        random.choice(string.ascii_lowercase +
                      string.digits + string.ascii_uppercase)
        for i in range(20)
    )

calibGlycolKey = postCalibGlycolKey
while calibGlycolKey == postCalibGlycolKey:
    calibGlycolKey = "".join(
        random.choice(string.ascii_lowercase +
                      string.digits + string.ascii_uppercase)
        for i in range(20)
    )

dirNum = 0 # counter for which search directory we are currently on
startTime = 0 # temp var to hold start and end time

isThreading = True # whether to use multithreading or not
threads = [] # list of threads to run

detectionList = {"FT2 SUM": [], "FT3": [], "FT2 RAW": [], "FT1": []} # the dict of preferences to look for
retrieveData = None # data from preferences.json
regions = [] # regions for ft2 sum
data = {} # used to store test data in, with the following format
# {
#     "sn1":{
#         "test1":{
#             data
#         },
#         "test2":{
#             data
#         }
#         ...
#     }
#     "sn2":{
#         "test1":{
#             data
#         },
#         "test2":{
#             data
#         }
#         ...
#     }
#     ...
# }
headers = [] # list of headers for output file
currentSN = None # serial number of current file being read
certdir = None # certificate directory
genCert = False # bool to determine whether or not to generate certificates
errors = [] # list of errors that occurred


def calc(fileName, dud):
    global currentSN, data, headers, errors
    try:
        fileType = getFileType(fileName) # get what type of file it is, returns "FT2 SUM", "FT1", ...
        # wasIn = False
        if fileType == "FT2 SUM": # parsing procedure if the filetype is FT2 SUM
            with open(fileName, newline="") as file:
                sn = None # serial number of device
                region = ""  # current region
                for row in csv.reader(file, delimiter="\n", quotechar=","):
                    for r in row:
                        v = r.split(",") # list of values in current row
                        if "SN" in v or "Serial Number" in v: # if "Sn" or "Serial Number" in current row
                            sn = v[1] # serial number will be in the second column
                            currentSN = sn # store currentSN
                            if sn not in data: # if the serial number doesn't already exists in data, then add it
                                data[sn] = {}
                            if fileName not in data[sn]: # if the fileName doesn't already exist for this serial number then add it, otherwise if it does (it shouldn't) exit the loop
                                data[sn][fileName] = {}
                            else:
                                break
                            _date = fileName.replace(".csv", "").split("_") # fileName by "_" removing file extension
                            index = 1 # index counter
                            for i in range(len(_date)): # find the index of where "SUM" is located, date should come before this
                                if "SUM" in _date[i]:
                                    index = i
                            _date = _date[index - 2] # get date relative to SUM location
                            data[sn][fileName]["Serial Number"] = sn # store serial number in data dict
                            data[sn][fileName]["Date"] = (
                                _date[4:6] + "/" +
                                _date[6:8] + "/" + _date[0:4]
                            ) # parse date into MM/DD/YYYY and store it
                            data[sn][fileName]["File Name"] = fileName.split(
                                "\\")[-1] # parse fileName and store it
                            data[sn][fileName]["Test Type"] = fileType # store file type
                            continue
                        elif sn == None: # if the serial number hasn't been found, then data can't be stored and continue
                            continue
                        if len(v) == 1: # if the current row is 1 cell wide, then this a region has started
                            region = v[0]
                            if region not in regions:
                                regions.append(region)
                        for i in detectionList["FT2 SUM"]: # loop through all the preferences
                            try: # try to get the required elements from the preference
                                index = i["column"] - 1 # index is the column-1 because numbers start at 0
                                dataField = i["title"] # dataField is the title we are looking for
                                dataKey = getTitle_config(i) # This is the title of the header that we want to store it under
                            except: # if one or more of the necessary elements can't be found, then return an error
                                raise Exception(
                                    "One or more required keys in an FT2 SUM preference are missing"
                                )

                            dataRegion = None if "region" not in i else i["region"] # current region if it exists in the current preference
                            if type(dataField) != list: # if the dataField is not a list of elements
                                if dataRegion == None and dataField == v[0]: # if preference is not regional and we are on the correct row
                                    # wasIn = (dataKey in data[sn][fileName]) # set flag
                                    data[sn][fileName][dataKey] = v[index] # store the data
                                elif dataRegion != None and (
                                    dataField in v and region == dataRegion
                                ): # if preference is regional and we are in the region, on the right row
                                    # wasIn = (dataKey in data[sn][fileName]) # set flag
                                    data[sn][fileName][dataKey] = (
                                        v[index] if v[index] != "" else "0"
                                    ) # store data if it is found, otherwise if the row exists, and there is no data in that column, then return a 0 (calibration not needed)

                            elif type(dataField) == list: # if the dataField is a list of elements
                                allIn = all([i in v for i in dataField]) # make sure that all elements of the preference's dataField are in the current row
                                if dataRegion == None and allIn: # non regional data in allin
                                    # wasIn = (dataKey in data[sn][fileName]) # set falg
                                    data[sn][fileName][dataKey] = v[index] # store data
                                elif dataRegion != None and (
                                    allIn and region == dataRegion
                                ): # if regional and allIn and in the correct region
                                    # wasIn = (dataKey in data[sn][fileName]) # set flag
                                    data[sn][fileName][dataKey] = (
                                        v[index] if v[index] != "" else "0"
                                    ) # store data if it is found, otherwise if the row exists, and there is no data in that column, then return a 0 (calibration not needed)

                if sn == None: # if a serial number isn't found then raise an error
                    raise Exception("Doesn't have a serial number")
        elif fileType == "FT3": # parsing for FT3
            with open(fileName, newline="") as file:
                ft3headers = None # the headers that are present at the top of the ft3 file
                sn = None # the current serial number of the row
                for row in csv.reader(file, delimiter="\n", quotechar=","):
                    for r in row:
                        v = r.split(",")
                        if ft3headers == None: # if the headers haven't been detected then the current row are the headers (this assumes that the first row, will always be the header)
                            ft3headers = v
                        else:
                            _date = "couldn't parse"
                            try:
                                _date = v[ft3headers.index("TimeStamp")].split(" ")[
                                    0] # attempt to parse the data from TimeStamp column, ignoring the time (assuming the date time is separated by a space)
                            except:
                                pass
                            sn = v[ft3headers.index("Serial Number")] # set the current sn
                            if sn not in data: # initialize the sn if it isn't already
                                data[sn] = {}
                            if fileName not in data[sn]: # initialize the fileName it isn't already
                                data[sn][fileName] = {}
                            data[sn][fileName]["Serial Number"] = sn # store the serial number under the filename
                            for i in detectionList["FT3"]: # loop through FT3 preferences
                                title = getTitle_config(i) # get the header to store the data under
                                dataField = i["title"] # get the title of the column to retrieve from
                                if dataField in ft3headers: # if the header exists in the ft3headers of this file, store it's data
                                    try:
                                        # wasIn = (title in data[sn][fileName])
                                        data[sn][fileName][title] = v[
                                            ft3headers.index(dataField)
                                        ]
                                    except:
                                        pass
                            data[sn][fileName]["File Name"] = fileName.split(
                                "\\")[-1] # store the filename
                            data[sn][fileName]["Date"] = _date # store the date
                            data[sn][fileName]["Test Type"] = fileType # store the file type
        elif fileType == "FT1": # parsing for FT1
            with open(fileName, newline="") as file:
                sn = None # current sn
                ft1headers = None # headers for ft1
                modelId = None # current model id
                travId = None # current traveller id
                for row in csv.reader(file, delimiter="\n", quotechar=","):
                    for r in row:
                        v = r.split(",")
                        if "Model ID" in v and len(v) > 1: # keep track of model id
                            modelId = v[1]
                        if "Traveller ID" in v and len(v) > 1: # keep track of traveller id
                            travId = v[1]
                        if "SN" in v or "Serial Number" in v: # check if current row is sn
                            sn = v[1] # get sn from second column
                            currentSN = sn # set currentSN
                            if sn not in data: # initialize this sn
                                data[sn] = {}
                            if fileName not in data[sn]: # initialize this file name
                                data[sn][fileName] = {}
                            data[sn][fileName]["Serial Number"] = sn # store sn
                            data[sn][fileName]["File Name"] = fileName.split(
                                "\\")[-1] # store filename
                            _date = fileName.replace(".csv", "").split("_")[-2] # get date (assuming this is the second last "_" separeted value ignoring the file extension)
                            data[sn][fileName]["Date"] = (
                                _date[2:4] + "/" + _date[4:6] +
                                "/20" + _date[0:2]
                            ) # parse date and store it
                            data[sn][fileName]["Test Type"] = fileType # store file type
                            continue # continue as there is no more data in this row
                        elif sn == None: # if there is no sn then continue (modelId or travellerId row)
                            continue
                        if len(v) > 2 and ft1headers == None: # store the ft1headers, this assumes that the first row with more than 2 values is the header
                            ft1headers = v
                        for i in detectionList["FT1"]: # loop through all FT1 preferences
                            try:
                                dataField = i["title"] # hheader to store data under
                                dataKey = getTitle_config(i) # title of column that data is stored under
                            except: # throw error if one ore more of these keys can't be found in preference
                                raise Exception(
                                    "One or more required keys in an FT1 preference are missing"
                                )

                            if ft1headers == None: # if the header hasn't been found yet (we are in the region of data that comes before the header)
                                if dataField == "Model ID" and modelId != None: # store model id
                                    # wasIn = (dataKey in data[sn][fileName])
                                    data[sn][fileName][dataKey] = modelId
                                elif dataField == "Traveller ID" and modelId != None: # store traveller id
                                    # wasIn = (dataKey in data[sn][fileName])
                                    data[sn][fileName][dataKey] = travId
                                elif dataField in v: # store the data of the current preference
                                    # wasIn = (dataKey in data[sn][fileName])
                                    data[sn][fileName][dataKey] = v[1]
                            elif "step" in i: # otherwise if "step" exists in the current preference (this assumes that all preferences retrieved from this bottom section have a "step" key)
                                step = i["step"] # get step name
                                if v[0] == step and dataField in ft1headers: # check if you are in the right row and retrieve data from desired column
                                    # wasIn = (dataKey in data[sn][fileName])
                                    data[sn][fileName][dataKey] = v[
                                        ft1headers.index(dataField) # problems may arise if there happens to be a duplicate header as .index() returns the first occurrance only
                                    ]

                if sn == None: # throw error if serial number can't be found
                    raise Exception(
                        "Doesn't have a serial number, possibly not a test file")
        elif fileType == "FT2 RAW": # no parsing for ft2
            return False
        else: # if a file type wasn't detecteds 
            return False

        # if(wasIn): # if an overwrite of data has occured throw an error
        # this may or may not be functioning code
        #     raise Exception("Overwriting has occured")

        return True
    except csv.Error as e: # ignore unicode errors
        pass
    except Exception as e: # log any errors that occured during the process
        logger.error(Exception(
            fileName
            + " couldn't be read with the following error:\n\n\t"
            + str(e)
            + "\n\n"
        ))

        # print(fileName + " couldn't be read with the following error: "+str(e))


def writeHeaderToFile(writer):
    # check for duplicates
    check = []
    duplicates = []
    dups = False
    for test in detectionList: # loop through all the preferences
        for i in detectionList[test]:
            try: # try to get title
                title = getTitle_config(i)
            except Exception as e:
                logger.error(e)
            if title not in check: # add title to check if it isn't already there
                check.append(title)
            elif title != daqTempKey and title != calibKey and title != testResKey and title != postDaqTempKey and title != postCalibKey and title != postCalibGlycolKey and title!=calibGlycolKey: # otherwise if it is already in check and it is not a certificate preference mark it as a duplicate  
                if title not in duplicates:
                    duplicates.append(title)
                dups = True

    if dups: # if duplicates exist print a warning
        print(
            "Be cautious of using duplicate headers, this may cause overwriting and loss of data:"
        )
        for i in duplicates:
            print(i)
        print()
        # raise Exception(
        #     "Cannot have duplicates in header. Please check your preferences.json and resolve issue. If there are not issues run the script again")
    for limav in (retrieveData["Avoid"] if "Avoid" in retrieveData else []) + (
        retrieveData["Limit"] if "Limit" in retrieveData else []
    ): # check to make sure "Test Type" is not in "Avoid" and "Limit" to avoid future errors
        for i in limav:
            if i == "Test Type":
                raise Exception(
                    'Cannot have "Test Type" as a "Limit" or "Avoid"')


def writeDataToFile(writer, dir, fileNames):
    global dirNum, threads, startTime
    if not isThreading and dirNum == 0: # store start time of retrieval
        startTime = time.time()
    dirNum += 1 # increment directory counter
    global certdir

    bar = tqdm(fileNames)
    if(not isThreading): # set the progress bar description based on whether threading is being used or not
        bar.set_description(
            "Retrieving from the %s directory" % ordinal(dirNum))
    else:
        bar.set_description(
            "Initializing for the %s directory" % ordinal(dirNum))

    for fileName in bar:
        ###
        if not isThreading: # retrieve data if not threading
            success = calc(fileName, 0)
        ###
        if isThreading: # add thread for retrieval if threading
            threads.append(threading.Thread(target=calc, args=(fileName, 0)))
        ###


def writeSummaryToFile(writer):
    global data, threads, startTime

    # execute threads
    if isThreading:
        startTime = time.time()
        runThreads(threads, 1000, "Retrieving Data") # execute threads
    # print("Retrieved in " + str(time.time() - startTime) + " seconds")

    # sort data
    # try:
    #     data = {
    #         k: v
    #         for k, v in sorted(
    #             data.items(),
    #             key=lambda sn: datetime.strptime(
    #                 str(dateutil.parser.parse(sn[1]["Date"])), "%Y-%m-%d %H:%M:%S"
    #             ),
    #         )
    #     }
    # except:
    #     pass  # print("Bad date exists, will not sort by date")
    
    # header calculating
    length = len(data)
    global headers
    bar = tqdm(data)
    bar.set_description("Processing Data")
    for sn in bar: # calculate list of headers based on keys in data dict
        for test in data[sn]:
            for header in data[sn][test]:
                if header not in headers and (
                    data[sn][test]["Test Type"]
                    in retrieveData["Master Summary File Tests"]
                ): # only include header if it is of the correct test type, this will exclude other test types from the summary file
                    headers.append(header)
    # rearrange the header to have Serial Number, Test Type, File Name, Date, FT1 headers, FT2 SUM headers, FT3 headers
    try: 
        for i in reversed([getTitle_config(j) for j in detectionList["FT3"]]):
            moveToBeginning(headers, i)
        for i in reversed([getTitle_config(j) for j in detectionList["FT2 SUM"]]):
            moveToBeginning(headers, i)
        for i in reversed([getTitle_config(j) for j in detectionList["FT1"]]):
            moveToBeginning(headers, i)
    except Exception as e:
        logger.error(e)
    moveToBeginning(headers, "Date")
    moveToBeginning(headers, "File Name")
    moveToBeginning(headers, "Test Type")
    moveToBeginning(headers, "Serial Number")
    # remove a preference from headers if it is supposed to be hidden
    # TODO: move this logic up to upper loop 
    for test in detectionList:
        for pref in detectionList[test]:
            if "hide" in pref and pref["hide"]:
                try:
                    title = getTitle_config(pref)
                except Exception as e:
                    logger.error(e)
                if title in headers:
                    headers.remove(title)
    # write out the header to the summary file
    writer.writerow(headers)
    # writing data
    validSn = [] # a list of valid serial numbers that is generated from Avoid/Limit for certificate generation
    bar = tqdm(data)
    bar.set_description("Writing Data")
    for sn in bar:
        for test in data[sn]: # fill in data with noDataStr if it doesn't already exist in data dict
            for h in headers:
                if h not in data[sn][test]:
                    data[sn][test][h] = noDataStr  

            if getSkippable(data[sn][test]): # run through Avoid/Limit code and check whether it is a valid row to write out/generate certificate for
                continue
            if sn not in validSn: # add sn to validSn since it hasn't been skipped
                validSn.append(sn)
            try: # write out data to summary file
                rowData = [data[sn][test][h] for h in headers]
                if(data[sn][test]["Test Type"] in retrieveData["Master Summary File Tests"]): # probably works without this
                    writer.writerow(rowData)
            except:
                pass
                # print("Couldn't write data for %s, Most likely due to non encodable characters in filename"%sn)

    if genCert: # if certificates are to be generated
        bar = tqdm(validSn)
        bar.set_description("Generating Certificates")
        for sn in bar:
            for test in data[sn]:
                try:
                    if (
                        "Date" in data[sn][test]
                        and testResKey in data[sn][test]
                        and (daqTempKey in data[sn][test] or postDaqTempKey in data[sn][test])
                        and (calibKey in data[sn][test] or postCalibKey in data[sn][test])
                    ): # check to make sure all required parts of the certificate are included
                        # if(not isThreading):
                        daqTemp = data[sn][test][postDaqTempKey] if postDaqTempKey in data[sn][test] else "N/A" # if the post calibration daq temperature is in data store it in daqTemp otherwise store N/A
                        calibTemp = data[sn][test][postCalibKey] if postCalibKey in data[sn][test] else "N/A" # if the post calibration calibration temperature is in data store it in daqTemp otherwise store N/A
                        if (calibTemp.isnumeric() and float(calibTemp) == 0) or calibTemp=="N/A": # if the calibTemp is 0 then use calibration values
                            calibTemp = data[sn][test][calibKey] if calibKey in data[sn][test] else "N/A"
                            daqTemp = data[sn][test][daqTempKey] if daqTempKey in data[sn][test] else "N/A"

                        # round calibTemp and daqTemp 
                        try:
                            calibTemp = str(round(float(calibTemp), 1))
                        except:
                            pass
                        try:
                            daqTemp = str(round(float(daqTemp), 1))
                        except:
                            pass

                        # if glycolTemp is present store it in post calibration, otherwise use calibration 
                        glycolTemp = data[sn][test][postCalibGlycolKey] if postCalibGlycolKey in data[sn][test] else ""
                        if glycolTemp == "" and calibGlycolKey in data[sn][test]:
                            glycolTemp = data[sn][test][calibGlycolKey]
                        # round glycolTemp
                        try:
                            glycolTemp = str(round(float(glycolTemp),1))
                        except:pass
                        # if glycolTemp is present then add them 
                        if glycolTemp != "":
                            calibTemp += "\n"+glycolTemp
                            daqTemp += "\n"+daqTemp
                        
                        
                        if data[sn][test][testResKey] != "Test Complete":continue # if the test failed then don't generate the certificate


                        # # # check to see if there is a glycol temp but no calibTemp
                        # if ("N/A" in calibTemp and glycolTemp!=""):
                        #     print(calibTemp,glycolTemp,data[sn][test][calibKey] if calibKey in data[sn][test] else "calibKey not found")
                        # continue
                        
                        # generate the certificate
                        createCertificate(
                            sn,
                            data[sn][test]["Date"],
                            "Pass"
                            if data[sn][test][testResKey] == "Test Complete"
                            else "Fail",
                            daqTemp,
                            calibTemp,
                            certdir,
                            logger,
                            header = glycolTemp!="" # boolean to determine whether or not to add Glycol Probe: to the row title or not
                        )
                        
                except Exception as e: # error handling
                    raise e
                    # logger.error(Exception(
                    #     "Couldn't generate certificate, check config file for correct preferences"
                    # ))
   

    if (
        "PDF Certificates" in retrieveData
        and retrieveData["PDF Certificates"] == True
        and "Generate Certificates" in retrieveData
        and retrieveData["Generate Certificates"] == True
    ): # generate pdf certificates if certificates were generated
        convertToPDF_path(certdir) # this will convert all pdfs in certdir to pdfs, loop through the ones you want and cuse convertToPDF_doc if you don't want this behaviour. It is uglier and slower


def init(cdir, pdir, odir, log):
    global certdir, preferencesFile, detectionList, retrieveData, genCert, outdir, logger, outFileName
    logger = log
    certdir = cdir
    preferencesFile = pdir
    outdir = odir
    try:
        with open(preferencesFile) as f:
            retrieveData = json.load(f)
            retrieveData["Master Summary File Tests"]
    except (PermissionError):
        logger.error(Exception(
            "Preferences file couldn't be opened. Close the file if it is open"
        ))
    except Exception as e:
        print("Invalid preferences JSON file, check syntax: " + str(e))
        exit()

    try:
        moveToBeginning(retrieveData["Master Summary File Tests"], "FT3")
        moveToBeginning(retrieveData["Master Summary File Tests"], "FT2 RAW")
        moveToBeginning(retrieveData["Master Summary File Tests"], "FT2 SUM")
        moveToBeginning(retrieveData["Master Summary File Tests"], "FT1")
        outFileName = "summary" + "_" + \
            "_".join(retrieveData["Master Summary File Tests"]) + ".csv"
        retrieveData["Test Preferences"].append(
            {
                "test": "FT2 SUM",
                "title": "DAQ Temperature (oC)",
                "region": "Post Calibration Data",
                "column": 2,
                "hide": True,
                "column header": postDaqTempKey,
            }
        )
        retrieveData["Test Preferences"].append(
            {
                "test": "FT2 SUM",
                "title": "Air1",
                "region": "Post Calibration Data",
                "column": 2,
                "hide": True,
                "column header": postCalibKey,
            }
        )
        retrieveData["Test Preferences"].append(
            {
                "test": "FT2 SUM",
                "title": "Glycol",
                "region": "Post Calibration Data",
                "column": 2,
                "hide": True,
                "column header": postCalibGlycolKey,
            }
        )

        retrieveData["Test Preferences"].append(
            {
                "test": "FT2 SUM",
                "title": "DAQ Temperature (oC)",
                "region": "Calibration Data",
                "column": 2,
                "hide": True,
                "column header": daqTempKey,
            }
        )
        retrieveData["Test Preferences"].append(
            {
                "test": "FT2 SUM",
                "title": "Air1",
                "region": "Calibration Data",
                "column": 2,
                "hide": True,
                "column header": calibKey,
            }
        )
        retrieveData["Test Preferences"].append(
            {
                "test": "FT2 SUM",
                "title": "Glycol",
                "region": "Calibration Data",
                "column": 2,
                "hide": True,
                "column header": calibGlycolKey,
            }
        )

        # retrieveData["Test Preferences"].append(
        #     {
        #         "test": "FT2 SUM",
        #         "title": "Air",
        #         "region": "Post Calibration Data",
        #         "column": 2,
        #         "hide": True,
        #         "column header": calibKey,
        #     }
        # )
        # retrieveData["Test Preferences"].append(
        #     {
        #         "test": "FT2 SUM",
        #         "title": "Air",
        #         "region": "Post Calibration Data",
        #         "column": 2,
        #         "hide": True,
        #         "column header": postCalibKey,
        #     }
        # )

        retrieveData["Test Preferences"].append(
            {
                "test": "FT2 SUM",
                "title": "TestResult",
                "column": 2,
                "hide": True,
                "column header": testResKey,
            }
        )

        for i in retrieveData["Test Preferences"]:
            if "test" not in i:
                logger.error(Exception(
                    'One or more of the "Test Preferences" don\'t contain a "test"'
                ))
            elif i["test"] not in detectionList:
                logger.error(Exception(
                    'One or more of the "Test Preferences" has an invalid "test" name'
                ))
            detectionList[i["test"]].append(i)

    except Exception as e:
        # raise Exception('No "Test Preferences" key in prefences file')
        logger.error(e)

    genCert = (
        "Generate Certificates" in retrieveData
        and retrieveData["Generate Certificates"]
    )


def getOutFileName():
    return outFileName


def getSkippable(row): # it works, leave it
    global retrieveData
    skip = False

    if "Limit" in retrieveData:
        limFound = None
        if type(retrieveData["Limit"]) != list:
            retrieveData["Limit"] = [retrieveData["Limit"]]
        if len(retrieveData["Limit"]) and type(retrieveData["Limit"][0]) == dict:
            for i in (
                retrieveData["Limit"]
                if type(retrieveData["Limit"]) == list
                else [retrieveData["Limit"]]
            ):  # looping through list of limits
                curr = []  # checks if the current key is fully part of said data field
                for lim in i:  # looping through keys in limits
                    if limFound == None:
                        limFound = False
                    if lim not in row and lim != "*":
                        # if the current is not in the data fields then it doesn't need to be limited, therefore it is not fully part of the data field
                        curr.append(False)
                    else:
                        if lim != "*":
                            curr.append(allIn(row[lim], i[lim]))
                        else:
                            curr.append(allInSome(row.values(), i[lim]))
                    if not all(curr):
                        break  # if the current key is not fully in the data field, then it doesn't need to be limited
                if all(curr):
                    limFound = True
            if limFound == False:
                skip = True

    if "Avoid" in retrieveData:
        if type(retrieveData["Avoid"]) != list:
            retrieveData["Avoid"] = [retrieveData["Avoid"]]
        if len(retrieveData["Avoid"]) and type(retrieveData["Avoid"][0]) == dict:
            skipAv = False
            for i in (
                retrieveData["Avoid"]
                if type(retrieveData["Avoid"]) == list
                else [retrieveData["Avoid"]]
            ):  # looping through list of avoids
                if not skipAv:
                    curr = (
                        []
                    )  # checks if the current key is fully part of said data field
                    for av in i:  # looping through keys in avoids
                        if av not in row and av != "*":
                            # if the current is not in the data fields then it doesn't need to be avoided, therefore it is not fully part of the data field
                            curr.append(False)
                        else:
                            if av != "*":
                                curr.append(allIn(row[av], i[av]))
                            else:
                                curr.append(allInSome(row.values(), i[av]))
                        if not all(curr):
                            break  # if the current key is not fully in the data field, then it doesn't need to be avoided
                    if all(curr) and curr != []:
                        skipAv = True
                if skipAv:
                    skip = True
                    break

    try:
        if "Dates" in retrieveData:
            isIn = len(retrieveData["Dates"]) == 0
            for i in retrieveData["Dates"]:
                snDate = dateutil.parser.parse(row["Date"])
                snDate = {"Day": snDate.day,
                          "Month": snDate.month, "Year": snDate.year}
                if "Day" not in i:
                    del snDate["Day"]
                if "Month" not in i:
                    del snDate["Month"]
                if "Year" not in i:
                    del snDate["Year"]

                same = True

                try:
                    same = same and snDate["Year"] == i["Year"]
                except:
                    pass

                try:
                    same = same and snDate["Day"] == i["Day"]
                except:
                    pass

                try:
                    same = same and snDate["Month"] == i["Month"]
                except:
                    pass

                if same and (i["test"] == row["Test Type"] if "test" in i else True):
                    isIn = True
            if not isIn:
                skip = True
    except:
        pass
    return skip
