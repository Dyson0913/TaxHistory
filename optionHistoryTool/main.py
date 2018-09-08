import os
from Tkinter import *
import datetime
import re
import requests
from datetime import date
import csv




class Application(Frame):


    def createWidgets(self):
        self.var = IntVar()
        self.var.set(1)
        c = Checkbutton(
            self, text="TXO",
            variable=self.var)

        c.pack()

        group = LabelFrame(self, text="time", padx=5, pady=5)
        group.pack(padx=10, pady=10)

        w = Label(group, text="data_Start")
        w.grid(row=0, column=1)
        #w.grid(row=0)
        w.pack(side=LEFT)

        today = datetime.date.today()
        self.databegin = Entry(group)
        self.databegin.insert(0,str(today))
        self.databegin.grid(row=0, column=1)
        self.databegin.pack(side=LEFT)

        end = Label(group, text="data_End")
        #end.grid(row=1)
        end.grid(row=1, column=1)
        end.pack(side=LEFT)

        self.dataend = Entry(group)
        self.dataend.insert(0, str(today))
        self.dataend.grid(row=1, column=1)
        self.dataend.pack(side=LEFT)

        dg = LabelFrame(self, text="week(pick target day)", padx=5, pady=5)
        dg.pack(side=LEFT,padx=10, pady=10)

        #MODES = [
        #    ("0", "0"),
        #    ("1", "1"),
        #    ("2", "2"),
        #    ("3", "3"),
        #    ("4", "4"),
        #    ("5", "5"),
        #    ("6", "6"),
        #]
        #self.dayV = StringVar()
        #self.dayV.set("0")  # initialize

        #for text, mode in MODES:
        #    b = Radiobutton(dg, text=text,
        #                    variable=self.dayV, value=mode)
        #    b.pack(anchor=W)

        ig = LabelFrame(self, text="ITM OTM", padx=5, pady=5)
        ig.pack(padx=10, pady=10)
        MODES = [
            ("ITM", "ITM"),
            ("OTM", "OTM"),
        ]
        self.tm = StringVar()
        self.tm.set("ITM")  # initialize

        for text, mode in MODES:
            b = Radiobutton(ig, text=text,
                            variable=self.tm, value=mode)
            b.pack(anchor=W)

        gb = LabelFrame(self, text="Atm(plus or sub)", padx=5, pady=5)
        gb.pack(padx=10, pady=10)

        MODES = [
            ("plusAtm", "plusAtm"),
            ("subAtm", "subAtm"),
        ]
        self.atmWay = StringVar()
        self.atmWay.set("plusAtm")  # initialize
        for text, mode in MODES:
            b = Radiobutton(gb, text=text,
                            variable=self.atmWay, value=mode)
            b.pack(anchor=W)

        vb = LabelFrame(self, text="priceVolume", padx=5, pady=5)
        vb.pack(padx=10, pady=10)

        self.priceVol = StringVar()
        self.priceVol.set("0")  # initial value
        option = OptionMenu(vb, self.priceVol, "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15")
        option.pack()

        self.QUIT = Button(self)
        self.QUIT["text"] = "Gentxt"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.parse
        self.QUIT.pack(fill=Y)

        self.stateS = StringVar()
        self.stateS.set("start = ready to create sheet")
        self.w = Label(self, textvariable=self.stateS)
        self.w.pack()

    def errorMsg(self,msg):
        top = Toplevel()
        top.title("error")
        msg = Message(top, text=msg)
        msg.pack()
        #button = Button(top, text="close", command=top.destroy)
        #button.pack()

    def datepare(self,str):
        matchObj = re.match(r'(\d+)\-(\d+)-(\d+)', str, re.M | re.I)
        return int(matchObj.group(1)) ,int(matchObj.group(2)) ,int(matchObj.group(3))

    def dateinputCheck(self, month, dat):
        if month > 12 or month <= 0:
            self.errorMsg("month error!! over 12 or < 0")
            return False

        if dat > 31 or dat <= 0:
            self.errorMsg("date error!! over 31 or < 0")
            return False

        return True

    def parse(self):
        #print "result ", self.var.get()

        year, month, mydate = self.datepare(self.databegin.get())
        eyear, emonth, emydate = self.datepare(self.dataend.get())

        #month check
        if self.dateinputCheck(month, mydate) == FALSE:
            return
        if self.dateinputCheck(emonth, emydate) == FALSE:
            return

        nowday = date(year, month, mydate)
        backday = date(eyear, emonth, emydate)

        # 0 = sunday
        self.anyday = datetime.datetime(year, month, mydate).strftime("%w")
        totalday = -(nowday-backday).days+1

        # count for now day
        oneday = datetime.timedelta(days=1)
        self.genDays = list()
        self.grabDays = list()
        for num in range(0, totalday):
            delta = datetime.timedelta(days=num)
            newday = backday - delta
            self.anyday = datetime.datetime(newday.year, newday.month, newday.day).strftime("%w")
            #print "%s  week %d %d" % (str(newday), int(self.anyday),(int(self.anyday) % 6 != 0 ))
            # 1~5
            #if int(self.anyday) % 6 != 0:
                #folder not exists, mk it
            if os.path.isdir(".\\data\\"+str(newday)) == False:
                self.genDays.append(newday)
                #print os.path.exists(".\\"+str(newday)+"\\"+str(newday)+".txt")
            self.grabDays.append(newday)


        #save file
        self.stateS.set("start = grab data....")
        self.saveFile()
        self.stateS.set("start = grab data ok")

        #load csv
        self.loadcsv()

    def loadcsv(self):

        stopdayname = '0'
        finalfileName = ""
        finalds = []

        for dateinfo in self.grabDays:
            #day filter
            weekday = datetime.datetime(dateinfo.year, dateinfo.month, dateinfo.day).strftime("%w")
            #if self.dayV.get() != weekday:
            #    continue

            today = str(dateinfo.year) + '/' + '{:02d}'.format(dateinfo.month) + "/" + '{:02d}'.format(dateinfo.day)
            # folder not exits, continue
            chckday = str(dateinfo.year) + '-' + '{:02d}'.format(dateinfo.month) + "-" + '{:02d}'.format(dateinfo.day)
            if os.path.isdir(".\\data\\" + str(chckday)) == False:
                continue

            stopdayname = str(dateinfo.year)
            wlist = []
            secdata = []
            path = ".\\data\\"+str(dateinfo)+"\\"+str(dateinfo)+".txt"
            f = open(path, 'rb')
            for row in csv.reader(f):
                #print row[2]
                wjudge = re.compile("("+stopdayname + "\\d\\d)(W(\\d))*")
                prematchObj = wjudge.match(row[2])

                #has w1 w2
                if prematchObj != None and prematchObj.group(2) != None:
                    pattern = re.compile("("+stopdayname+"\\d\\d)(W(\\d))*")
                    matchObj = pattern.match(row[2])
                    if matchObj != None:
                        secdata.append(row)
                        #print matchObj.group(2)
                        #print row[2]
                        if matchObj.group(3) not in wlist:
                            wlist.append(matchObj.group(3))
                elif prematchObj != None and prematchObj.group(2) == None:
                    #w3 only get like 201808 ,
                    if len(wlist) != 0:
                        continue
                    daymatch = str(dateinfo.year) + '{:02d}'.format(dateinfo.month)
                    if row[2] == daymatch:
                        secdata.append(row)

            f.close()

            semifinaldata =[]
            #del old w
            if len(wlist) > 0:
                for row in secdata:
                    depe = re.compile("(" + stopdayname + "\\d\\d)(W" + wlist[len(wlist)-1] + ")")
                    Obj = depe.match(row[2])
                    if Obj != None:
                        semifinaldata.append(row)
            else:
                #w3 only keep "normal data", not after pan data
                for row in secdata:
                    if row[17] == '\xa4@\xaf\xeb':
                        semifinaldata.append(row)

            #print semifinaldata
            #check lowest price
            n = len(semifinaldata)

            plusmidprice = []
            submidprice = []
            for i in range(0,n,2):
                calldata = semifinaldata[i]
                putdata = semifinaldata[i+1]
                callprice = 0
                putprice = 0
                if calldata[5] == '-':
                    callprice = 0
                elif putdata[5] == '-':
                    putprice = 0
                else:
                    callprice = float(calldata[5])
                    putprice = float(putdata[5])

                plusmidprice.append(callprice + putprice)
                submidprice.append(abs(callprice - putprice))

            print plusmidprice
            print submidprice
            print plusmidprice.index(max(plusmidprice))
            print submidprice.index(max(submidprice))

            #pick priveVol dataformat
            #0 1
            #2 3
            #4 5
            midpox = 0
            putpox = 0
            #print "atm", self.atmWay.get()
            if self.atmWay.get() == 'plusAtm':
                midpox = plusmidprice.index(max(plusmidprice))
            else:
                putpox = submidprice.index(max(submidprice))
            midpox *= 2
            putpox *= 2 +1

            # shift to get
            # call in -2 ,-4.... out +2,+4
            if self.tm.get() == "ITM":
                midpox -= int(self.priceVol.get()) * 2
                putpox += int(self.priceVol.get()) * 2
            else:
                midpox += int(self.priceVol.get()) * 2
                putpox -= int(self.priceVol.get()) * 2


            #out put data
            getpo = len(semifinaldata)
            if midpox > getpo or midpox < 0:
                continue

            data = semifinaldata.pop(midpox)
            print "call " + str(data)
            if data[5] == '-':
                continue

            print n
            print putpox
            print len(semifinaldata)

            if putpox > getpo or putpox < 0:
                continue
            putdata = semifinaldata.pop(putpox)
            print "put " + str(putdata)
            if putdata[5] == '-':
                continue

            findata =[]
            if weekday == "0":
                weekday = "7"

            findata.append(data[0])
            findata.append(weekday)
            findata.append(data[3])
            findata.append(data[5])
            findata.append(data[6])
            findata.append(data[7])
            findata.append(data[8])

            findata.append(putdata[5])
            findata.append(putdata[6])
            findata.append(putdata[7])
            findata.append(putdata[8])

            print findata

            ds = ",".join(findata)
            ds +="\r\n"
            finalds.append(ds)
        finalfileName = "week" + "_" + self.tm.get() + "_" + self.atmWay.get() + "_" + self.priceVol.get()
        fp = open(".\\" + finalfileName + ".txt", "wb")
        for item in finalds:
            fp.write(item)

        fp.close()



    def saveFile(self):

        for dateinfo in self.genDays:
            rdateStart = str(dateinfo.year) + '/' + '{:02d}'.format(dateinfo.month) + "/" + '{:02d}'.format(dateinfo.day)
            rdateEnd = str(dateinfo.year) + '/' + '{:02d}'.format(dateinfo.month) + "/" + '{:02d}'.format(dateinfo.day)
            my_data = {'DATA_DATE': rdateStart, 'DATA_DATE1': rdateEnd, 'datestart': rdateStart, 'dateend': rdateEnd,'COMMODITY_ID': 'TXO', 'his_year': '2017'}
            #print my_data
            r = requests.post('http://www.taifex.com.tw/chinese/3/3_2_3_b.asp', data=my_data)
            self.stateS.set("grab data "+rdateStart)
            # print r.status_code
            # print r.content
            if self.nodata(re.sub('\r\n', '', r.content)):
                continue

            os.makedirs(".\\data\\"+str(dateinfo))
            #save file
            fp = open(".\\data\\"+str(dateinfo)+"\\"+str(dateinfo)+".txt", "wb")
            fp.write(r.content)
            fp.close()

    def nodata(self, str):
        matchObj = re.match('(.+)', str)
        # print matchObj.endpos
        if matchObj.endpos == 441:
            return True
            return False

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()




root = Tk()
root.geometry("800x600")
app = Application(master=root)

app.mainloop()

#self.var = IntVar()
#c = Checkbutton(
#    self, text="Enable Tab",
#    variable=self.var,
#    command=self.cb,
#    state='active')
#c.pack()


#def cb(self):
#    print "variable is", self.var.get()

# list
#self.listbox = Listbox(self)
#self.listbox.pack()
# self.listbox.insert(END, "a list entry")

#for item in ["TXTai"]:
#    self.listbox.insert(END, item)

#button--------------------------
#self.hi_there = Button(self)
#self.hi_there["text"] = "Hello",
#self.hi_there["command"] = self.say_hi
#self.hi_there.pack(side=RIGHT)


