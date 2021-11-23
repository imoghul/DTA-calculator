ten = 0.0069444444452528800000000
one=ten/10

times = [44522.6778357407000000000000
,44522.6785419907
,44522.6792482755
,44522.6799545139
,44522.680660787

,44522.6813670486
,44522.6820733102
,44522.6827796065
,44522.6834860417
,44522.6841925116
,44522.6848987732
]
temps=[18.4
,17.3
,16.4
,15.6
,14.8

,14
,13.3
,12.5
,11.8
,11.2
,10.5
]

time0=times[0]
time1=min(times, key=lambda x:abs(x-(time0+ten)))
time2=min(times, key=lambda x:abs(x-(time0+ten*2)))
time3=min(times, key=lambda x:abs(x-(time0+ten*3)))
time4=min(times, key=lambda x:abs(x-(time0+ten*4)))
time5=min(times, key=lambda x:abs(x-(time0+ten*5)))
time6=min(times, key=lambda x:abs(x-(time0+ten*6)))
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

print(dta1)
print(dta2)
print(dta3)
print(dta4)
print(dta5)
print(dta6)
