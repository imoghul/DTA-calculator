import csv, glob, os
from numpy import mean

fileNames = glob.glob("*RAW.csv")
fileNames.sort()

dtToMin = lambda y,mon,d,h,m,s:(525600 * y + 43800 * mon + 1440 * d + 60 * h + m + s / 60)
# print("Choose a file: ")
# for i in range(len(fileNames)):
#   print(i,": ",fileNames[i])
# x=int(input("Enter file number: "))
# fileNames=[fileNames[2]]
def readTime(dt):  # takes input in the format of      Hour:Min:Sec (A/P)M Month/Day/Year
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
                        v[6]))  # 2 for thermocouple or 6 for slug
                    roomTemps.append(float(v[3]))

    time0 = times[0]
    ind0 = (times.index(time0))
    temp0 = temps[ind0]
    prev = 0
    for i in range(1, 6+1):
        timeout = i * 10
        t = min(times, key=lambda x: abs(x - (time0 + timeout)))
        ind = times.index(t)
        # dta = (temps[ind]-temps[ind0])/((t-time0))
        dta = abs(temps[ind] - temp0)
        tError = abs((t-time0)-timeout)
        # print(tError)
        if (dta == prev or  tError >= .5): break
        prev = dta
        dtas.append(dta)
    return (mean(roomTemps), dtas)


for fileName in fileNames:
  try:
    (roomTemp, dtas) = calc(fileName)
    print("%s\n\nAverage room temp:\n%f\nDTAs:" % (fileName[13:24], roomTemp))
    for i in dtas:
        print(i)
    print("\n\n\n")
    # os.remove(fileName)
  except:
    print(fileName+" couldn't be read")