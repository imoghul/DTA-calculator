# from numpy import mean

def ordinal(n):
    return "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

def empty():
    pass

def mean(x):
    sum = 0
    for i in x: sum+=i
    return sum/len(x)

def average(x):
    if len(x) == 0:
        return 0
    return mean(x)


def dtToMin(y, mon, d, h, m, s): return (525600 * y + 43800 * mon + 1440 * d + 60
                                         * h + m + s / 60)


def closestTo(arr, val):
    v = min(arr, key=lambda x: abs(x - val))
    return (v, arr.index(v))


def readTime(dt):  # sample dt: 3:09:12.039 PM 11/24/2021
    dt = dt.split(" ")
    d = dt[2]
    d_arr = (d.split("/"))
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


def process_bar(process,current, total,message = "",bar_length=15):
    fraction = current/total
    arrow = int(fraction*bar_length-1)*'-'+'>'
    padding = int(bar_length-len(arrow))*' '
    ending = '\n' if current==total else '\r'
    print(f'{process}:\t[{arrow}{padding}] {int(fraction*100)}%  :  {current}/{total} ; {message}',end = ending)


def parseSUMfileName(fileName):
    data = {}
    _date = fileName.split("_")[-3]
    data["Date"] =  _date[4:6]+"/"+_date[6:8]+"/"+_date[0:4]
    return data

def getFileType(fileName):
    if("_SUM" in fileName):
        return "FT2 SUM"
    elif("_RAW" in fileName):
        return "FT2 RAW"
    elif("FT3_" in fileName or "ft3_" in fileName):
        return "FT3"
    else: return "FT1" 

def moveToBeginning(l,elem):
    l.insert(0, l.pop(l.index(elem)))

def getFT2SUMTitle(d):
    return ((d["region"]+":") if "region" in d else "")+(d["title"])+((":"+d["column header"])if "column header" in d else "")