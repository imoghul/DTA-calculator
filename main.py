import csv, glob, os, sys
from numpy import mean

dtToMin = lambda y, mon, d, h, m, s: (525600 * y + 43800 * mon + 1440 * d + 60
                                      * h + m + s / 60)

dtasToCalc = 6


def average(x):
    if len(x) == 0: return 0
    return mean(x)


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
    if (dt[1] == "PM"):
        if h != 12:
            h += 12
    if (dt[1] == "AM"):
        if h == 12:
            h = 0
    return (year, month, day, h, m, s)


def calc(fileName):
    times = []
    temps = []
    dtas = []
    roomTemps = []
    isReading = False
    with open(fileName, newline='') as file:
        for row in csv.reader(file, delimiter='\n', quotechar=','):
            for r in row:
                v = r.split(',')
                if v[1] == "Pre-PullDown": isReading = True
                if v[1] == "Calibration": isReading = False
                if (isReading and len(v) == 7):
                    (year, month, day, h, m, s) = readTime(v[0])
                    num = dtToMin(year, month, day, h, m, s)
                    times.append(num)
                    temps.append(float(
                        v[2]))  # 2 for thermocouple or 6 for slug
                    roomTemps.append(float(v[3]))

    time0 = times[0]
    ind0 = (times.index(time0))
    temp0 = temps[ind0]
    prev = 0
    for i in range(1, dtasToCalc + 1):
        timeout = i * 10
        t = min(times, key=lambda x: abs(x - (time0 + timeout)))
        ind = times.index(t)
        # dta = (temps[ind]-temps[ind0])/((t-time0))
        dta = abs(temps[ind] - temp0)
        tError = abs(t - time0 - timeout)
        # print(tError)
        if (dta == prev or tError >= .6): break
        prev = dta
        dtas.append(dta)
    return (average(roomTemps), dtas)


DTAs = []
with open("results.csv", mode="w", newline="") as out:
    writer = csv.writer(out)
    writer.writerow([
        "Test", "Serial Number", "Date", "Time", "Average Room Temp.", "DTA1",
        "DTA2", "DTA3", "DTA4", "DTA5", "DTA6"
    ])
    if len(sys.argv) > 1:
        dirs = sys.argv[1:]
    else:
        dirs = [os.getcwd()]
    original = os.getcwd()
    for dir in dirs:
        os.chdir(dir)
        fileNames = glob.glob("*RAW*.csv", recursive=True)
        fileNames.sort()
        for fileName in fileNames:
            outlist = [dir]
            try:
                (roomTemp, dtas) = calc(fileName)
                DTAs.append(dtas)
                filelist = fileName.split("_")
                outlist.append(filelist[1])
                _date = filelist[3]
                d = _date[4:6] + "/" + _date[6:] + "/" + _date[0:4]
                outlist.append(d)
                outlist.append(filelist[4])
                outlist.append(roomTemp)
                for i in dtas:
                    outlist.append(str(i))
                print(outlist)
                writer.writerow(outlist)
            except:
                print(fileName + " couldn't be read")
        os.chdir(original)
    writer.writerow([])

    avgList = [
        "",
        "",
        "",
        "",
        "Average DTAs: ",
    ]
    for i in range(dtasToCalc):
        avgList.append(average([d[i] for d in DTAs if len(d) > i]))
    writer.writerow(avgList)
