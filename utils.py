from numpy import mean


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


def editList(l):    
    inp=" "
    while(inp!=""):
        print()
        for i in range(len(l)):
            print("%d: %s"%(i,l[i]))
        print()

        inp = str(input("to add an element type the exact name and column number separated by an @\nfor sub categories enter region:value\nfor example to get calibration glycol you type: Calibration Data:Glycol@5\nto remove an element type r and the number, for example: r 1\nto end press enter\ninput: "))
        
        if(inp==""):
            continue
        if(inp[0]=="r"):
            l.pop(int(inp.split(" ")[1]))
        else:
            l.append(inp)
        
    return l


def process_bar(current, total,bar_length=20):
    fraction = current/total
    arrow = int(fraction*bar_length-1)*'-'+'>'
    padding = int(bar_length-len(arrow))*' '
    ending = '\n' if current==total else '\r'
    print(f'Progress: [{arrow}{padding}] {int(fraction*100)}%  :  {current}/{total}',end = ending)