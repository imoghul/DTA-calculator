# from numpy import mean
import copy
import csv
from fileinput import filename
from tqdm import tqdm


def ordinal(n):  # convert int num to ordinal string
    return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10:: 4])


def empty():
    pass


def mean(x):  # calculate mean
    sum = 0
    for i in x:
        sum += i
    return sum / len(x)


def average(x):  # calculate mean without throwing an error due to empty list
    if len(x) == 0:
        return 0
    return mean(x)


def dtToMin(y, mon, d, h, m, s):  # convert date time to minutes
    return 525600 * y + 43800 * mon + 1440 * d + 60 * h + m + s / 60


def closestTo(arr, val):  # find the elemnt of a list of numbers that is closest to val
    v = min(arr, key=lambda x: abs(x - val))
    return (v, arr.index(v))


def readTime(dt):  # sample dt: 3:09:12.039 PM 11/24/2021 converted to tuple
    dt = dt.split(" ")
    d = dt[2]
    d_arr = d.split("/")
    t = dt[0]
    year = int(d_arr[2])
    month = int(d_arr[0])
    day = int(d_arr[1])
    h = int(t.split(":")[0])
    m = int(t.split(":")[1])
    s = float(t.split(":")[2])
    if (dt[1] == "PM") & h != 12:
        h += 12
    if (dt[1] == "AM") & h == 12:
        h = 0
    return (year, month, day, h, m, s)


# custom process bar; depricated
def process_bar(process, current, total, message="", bar_length=25, bar_pos=40 * " "):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * "-" + ">"
    padding = int(bar_length - len(arrow)) * " "
    ending = "\n" if current == total else "\r"

    padTable = ""
    while (len(f"{process}:" + padTable)) < len(bar_pos):
        padTable += " "
    print(
        f"{process}:{padTable}[{arrow}{padding}] {int(fraction*100)}%  :  {current}/{total} ; {message}",
        end=ending,
    )


def parseSUMfileName(fileName):  # retrieve data from fileName for ft2sum
    data = {}
    _date = fileName.split("_")[-3]
    data["Date"] = _date[4:6] + "/" + _date[6:8] + "/" + _date[0:4]
    return data


def getFileType(fileName):  # return file type
    if "_SUM" in fileName:
        return "FT2 SUM"
    elif "_RAW" in fileName:
        return "FT2 RAW"
    elif "FT3_" in fileName or "ft3_" in fileName:
        return "FT3"
    else:  # if cell A1 is "Model ID" or "Traveller ID" return "FT1"
        with open(fileName, newline="") as file:
            for row in csv.reader(file, delimiter="\n", quotechar=","):
                for r in row:
                    v = r.split(",")
                    if(v[0] == "Model ID" or v[0] == "Traveller ID"):
                        return "FT1"
                    else:
                        return None


def moveToBeginning(l, elem):  # move an element of a list to the beginning of it
    if elem not in l:
        return
    l.insert(0, l.pop(l.index(elem)))


def getFT2SUMTitle_noCH(d):  # return header of a preference, ignoring column header
    try:
        return ((d["region"] + ":") if "region" in d else "") + (
            ("_".join(d["title"]) if type(d["title"]) == list else d["title"])
        )
    except:
        raise Exception(
            'One or more entries in FT2 SUM don\'t contain the necessary "title" field'
        )


def getFT2SUMTitle_config(d):  # return header of an FT2 SUM preference
    return getFT2SUMTitle_noCH(d) if "column header" not in d else d["column header"]


def getFT3Title_config(d):  # return header of an FT3 preference
    try:
        return d["title"] if "column header" not in d else d["column header"]
    except:
        raise Exception(
            'One or more entries in FT3 don\'t contain the necessary "title" field'
        )


def getFT1Title_config(d):  # return header of an FT1 preference
    try:
        return (
            (((d["step"] + ":") if "step" in d else "") + d["title"])
            if "column header" not in d
            else d["column header"]
        )
    except:
        raise Exception(
            'One or more entries in FT1 don\'t contain the necessary "title" field'
        )


def getTitle_config(d):  # get column header of a preference
    try:
        res = None
        if "column header" in d:
            return d["column header"]
        elif d["test"] == "FT2 SUM":
            res = getFT2SUMTitle_config(d)
        elif d["test"] == "FT3":
            res = getFT3Title_config(d)
        elif d["test"] == "FT1":
            res = getFT1Title_config(d)

        return d["test"] + ":" + res
    except Exception as e:
        raise e
        return None


# def getFT2SUMTitle_raw(title, columnheader=None, region=None):
#     return (((region+":") if region != None else "")+(("_".join(title) if type(title) == list else title)))if columnheader == None else "column header"


def anyIn(val, l):  # checks if any of the elements of l are in val
    return True in [(i in val) for i in l]


def allIn(val, l):  # check if all of elements of val are in l
    return all([(i in val) for i in l])


def allInSome(targets, finds):  # checks if atleast 1 element of targets are in finds
    return True in [allIn(i, finds) for i in targets]


# takes data[sn], and returns its data; depricated data format
def getFromData(data, title):
    vals = []
    for i in data:
        if title in data:
            vals.append(data[title])
    return vals if vals != [] else None


# adds to data[sn]; depricated data format
def addToData(data, title, val, sn):
    added = False
    for i in data:
        if title not in i:
            i[title] = val
            added = True
            break
    if not added:
        if title == "Serial Number":
            data.append({"Serial Number": sn})
        else:
            data.append({"Serial Number": sn, title: val})


# run a list of threads limiting to a max number of threads at once
def runThreads(threads, max, message):
    originalMax = max
    upperMax = 15000
    processing = []
    dead = []
    length = len(threads)
    counter = 0
    with tqdm(total=length) as pbar:
        pbar.set_description(message)
        while counter < length:
            allAlive = True
            while len(processing) < max and len(threads):
                t = threads.pop(0)
                t.start()
                processing.append(t)

            for i in processing:
                if not i.is_alive():
                    counter += 1
                    pbar.update(1)
                    dead.append(processing.pop(processing.index(i)))
                    allAlive = False

            # if allAlive:
            #     # if(max < upperMax):
            #         max += 10
            # elif max > originalMax:
            #     max -= 1

    for t in dead + processing:
        t.join()
