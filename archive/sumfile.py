import csv,glob,os
from numpy import mean


fileNames=glob.glob("*SUM.csv")
fileNames.sort()
# print("Choose a file: ")
# for i in range(len(fileNames)):
#   print(i,": ",fileNames[i])
# x=int(input("Enter file number: "))
# fileName=fileNames[x]
def calc(fileName):
  times=[]
  temps=[]
  roomTemps=[0]
  isReading=False;
  with open(fileName,newline='') as file:
    for row in csv.reader(file,delimiter='\n',quotechar=','):
      for r in row:
        v=r.split(",")
        if(v[0]=="Pre-PullDown UUT Sampling"):isReading=True
        if(isReading):
          dt = v[1].split("T")
          d = dt[0].split("-")
          t = dt[1].split(":")
          year = int(d[0])
          month = int(d[1])
          day = int(d[2])
          h = int(t[0])
          m = int(t[1])
          s = float(t[2])
          num=(525600*year+43800*month+1440*day+60*h+m+s/60)
          times.append(num)
          temps.append(float(v[3]))

  time0=times[0]
  ind0=(times.index(time0))
  print("%s\n\nAverage room temp:\n%f\nDTAs:"%(fileName[13:24],mean(roomTemps)))
  prev=0
  for i in range(10,60,10):
    t = min(times, key=lambda x:abs(x-(time0+i)))
    ind = times.index(t)
    # dta = (temps[ind]-temps[ind0])/((t-time0))
    dta = abs(temps[ind]-temps[ind0])
    tError=abs(t-time0)%10
    if(dta==prev or (tError<=9 and tError>=1)):break;
    prev = dta
    print(dta)
  print("\n\n\n")
for fileName in fileNames:
  calc(fileName)
# os.remove(fileName)