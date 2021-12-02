
# with open("dta results.csv", mode="w", newline='') as out:
#     writer = csv.writer(out)
#     #output header to csv
#     header = [
#         "Test", "Serial Number", "Date", "Time", "Average Room Temp."]
#     for i in range(dtasToCalc):
#       header.append("DTA"+str(i+1))
#     writer.writerow(header)

#     # get list of directories to run
#     if len(sys.argv) > 1:
#         dirs = sys.argv[1:]
#     else:
#         dirs = [os.getcwd()]
#     original = os.getcwd()

#     for dir in dirs:
#         os.chdir(dir)
#         fileNames = glob.glob("*RAW*.csv", recursive=True)
#         fileNames.sort()
        
#         for fileName in fileNames:
#             outlist = [dir]
#             try:
#                 (roomTemp, dtas) = calc(fileName)
#                 DTAs.append(dtas)
#                 filelist = fileName.split("_")
#                 outlist.append(filelist[1])
#                 if (len(filelist) >= 5):
#                     _date = filelist[len(filelist)-3]
#                     d = _date[4:6] + "/" + _date[6:] + "/" + _date[0:4]
#                     outlist.append(d)
#                     outlist.append(filelist[len(filelist)-2])
#                 else:
#                     outlist.append("")
#                     outlist.append("")
#                 outlist.append(roomTemp)
#                 for i in dtas:
#                     outlist.append(str(i))
#                 print(outlist)
#                 writer.writerow(outlist)
#             except:
#                 print(fileName + " couldn't be read")
        
#         os.chdir(original) # return to original dir
#     writer.writerow([])

#     avgList = [
#         "",
#         "",
#         "",
#         "",
#         "Average DTAs: ",
#     ]
#     for i in range(dtasToCalc):
#         avgList.append(round(average([d[i] for d in DTAs if len(d) > i]), 1))
#     writer.writerow(avgList)
