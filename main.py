import csv,glob,os
from numpy import mean

times=[]
temps=[]
roomTemps=[]
isReading=False;
fileName=glob.glob("*.csv")[0]
with open(fileName,newline='') as file:
  for row in csv.reader(file,delimiter='\n',quotechar=','):
    for r in row:
      v = r.split(',')  
      if v[1]=="Pre-PullDown": isReading=True
      if v[1]=="Calibration": isReading=False
      if(isReading and len(v)==7):
        dt=v[0]
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
        if(dt[1]=="PM"):
          if h!=12:
            h += 12
        if(dt[1]=="AM"):
          if h==12:
            h = 0
        num=(525600*year+43800*month+1440*day+60*h+m+s/60)
        times.append(num)
        temps.append(float(v[2]))
        roomTemps.append(float(v[3]))





time0=times[0]
ind0=(times.index(time0))
print("%s\n\nAverage room temps:\n%f\nDTAs:"%(fileName[13:24],mean(roomTemps)))
for i in range(10,60,10):
  t = min(times, key=lambda x:abs(x-(time0+i)))
  ind = times.index(t)
  # dta = (temps[ind]-temps[ind0])/((t-time0))
  dta = abs(temps[ind]-temps[ind0])
  print(dta)

os.remove(fileName)