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
time1=min(times, key=lambda x:abs(x-(time0+10)))
time2=min(times, key=lambda x:abs(x-(time0+20)))
time3=min(times, key=lambda x:abs(x-(time0+30)))
time4=min(times, key=lambda x:abs(x-(time0+40)))
time5=min(times, key=lambda x:abs(x-(time0+50)))
time6=min(times, key=lambda x:abs(x-(time0+60)))
ind0=(times.index(time0))
ind1=(times.index(time1))
ind2=(times.index(time2))
ind3=(times.index(time3))
ind4=(times.index(time4))
ind5=(times.index(time5))
ind6=(times.index(time6))
# dta1 = (temps[ind1]-temps[ind0])/((time1-time0)/one)
# dta2 = (temps[ind2]-temps[ind0])/((time2-time0)/one)
# dta3 = (temps[ind3]-temps[ind0])/((time3-time0)/one)
# dta4 = (temps[ind4]-temps[ind0])/((time4-time0)/one)
# dta5 = (temps[ind5]-temps[ind0])/((time5-time0)/one)
# dta6 = (temps[ind6]-temps[ind0])/((time6-time0)/one)
dta1 = abs(temps[ind1]-temps[ind0])
dta2 = abs(temps[ind2]-temps[ind0])
dta3 = abs(temps[ind3]-temps[ind0])
dta4 = abs(temps[ind4]-temps[ind0])
dta5 = abs(temps[ind5]-temps[ind0])
dta6 = abs(temps[ind6]-temps[ind0])
print("Average room temps:\n%f\nDTAs:"%mean(roomTemps))
print(dta1)
print(dta2)
print(dta3)
print(dta4)
print(dta5)
print(dta6)
os.remove(fileName)