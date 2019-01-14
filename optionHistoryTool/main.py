import os
from Tkinter import *
import datetime
import re
import requests
from datetime import date
import csv
from bs4 import BeautifulSoup



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
        SelecModes = [
            ("interval", "interval"),
            ("point", "point"),
        ]
        self.interval = StringVar()
        self.interval.set("interval")  # initialize
        for text, mode in SelecModes:
            b = Radiobutton(vb, text=text,
                            variable=self.interval, value=mode)
            b.pack(side=LEFT)

        self.priceVol = StringVar()
        self.priceVol.set("0")  # initial value
        option = OptionMenu(vb, self.priceVol, "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15")
        option.pack(side=TOP)

        self.pointInterval = Entry(vb)
        self.pointInterval.insert(0, str(100))
        self.pointInterval.grid(row=0, column=1)
        self.pointInterval.pack(side=BOTTOM)


        gSett = LabelFrame(self, text="settledays", padx=5, pady=5)
        gSett.pack(padx=10, pady=10)

        self.settleday = IntVar()

        c = Checkbutton(gSett, text="settle", variable=self.settleday)
        c.pack()

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

            #folder not exists, mk it
            if os.path.isdir(".\\data\\"+str(newday)) == False:
                self.genDays.append(newday)
                #print os.path.exists(".\\"+str(newday)+"\\"+str(newday)+".txt")
            self.grabDays.append(newday)

        #if check settle , just parse filter day
        self.settlefilter()

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
                wjudge = re.compile("(\\d\\d\\d\\d\\d\\d)(W(\\d))*")
                prematchObj = wjudge.match(row[2])

                #has w1 w2
                if prematchObj != None and prematchObj.group(2) != None:
                    pattern = re.compile("(\\d\\d\\d\\d\\d\\d)(W(\\d))*")
                    matchObj = pattern.match(row[2])
                    if matchObj != None:
                        #"normal data", not after pan data
                        if row[17] != '\xbdL\xab\xe1':
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
                    if row[2].strip() == daymatch:
                        secdata.append(row)

            f.close()

            semifinaldata =[]
            #del old w
            if len(wlist) > 0:
                #w4 prejudge
                if len(wlist) == 1:
                    semifinaldata = self.filterw4(secdata)
                else:
                    for row in secdata:
                        #wlist w4,w1,get w4, modify to get last
                        depe = re.compile("(" + "\\d\\d\\d\\d\\d\\d)(W" + wlist[1] + ")")
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

            if n == 0:
                self.errorMsg("no match data ,output empty file")
                continue

            plusmidprice = []
            submidprice = []
            callminNum = 99998
            addminCnt = 1
            putminNum = 99998
            subminCnt = 1

            #check un-normal decline (like 2016/5/5 wired , 288-> 104-> 196)
            callplist =[]
            putplist =[]
            callsortvalue = 99999
            doublePriceValue = -1;
            doublePriceValueSub = -1;
            for i in range(0,n,2):
                calldata = semifinaldata[i]
                putdata = semifinaldata[i+1]
                callprice = 0
                putprice = 0
                if calldata[5] == '-':
                    callprice = 99999
                else:
                    callprice = float(calldata[5])
                callplist.append(callprice)

                if putdata[5] == '-':
                    putprice = 99999
                else:
                    putprice = float(putdata[5])
                putplist.append(putprice)
                    #callsortvalue = callprice - 0.1

                add = callprice + putprice
                plusmidprice.append(add)
                if add == callminNum:
                    addminCnt += 1
                    doublePriceValue = i/2
                if add < callminNum:
                    callminNum = add

                #when using sub condition, call - and put - will be zero, cause judge error, so fix it
                if callprice == 99999 and putprice == 99999:
                    sub = 99999
                else:
                    sub = abs(callprice - putprice)

                submidprice.append(sub)
                if sub == putminNum:
                    subminCnt += 1
                    doublePriceValueSub = i/2
                if sub < putminNum:
                    putminNum = sub

            print plusmidprice
            print submidprice
            print plusmidprice.index(min(plusmidprice))
            print submidprice.index(min(submidprice))

            #pick priveVol dataformat
            #0 1
            #2 3
            #4 5
            midpox = 0
            putpox = 0
            outSec = False
            if self.atmWay.get() == 'plusAtm':
                midpox = self.adjustWiredmidprice(plusmidprice,callplist,putplist,0) #plusmidprice.index(min(plusmidprice))
                putpox = midpox

                # two same price ,ITM put shift 2
                if addminCnt == 2 and int(self.priceVol.get()) == 0:
                    # two price the same,judge is the min
                    if doublePriceValue - plusmidprice.index(min(plusmidprice)) == 1:
                        outSec = True
            else:
                midpox = self.adjustWiredmidprice(submidprice,callplist,putplist,1) #submidprice.index(min(submidprice))
                putpox = midpox

                # two same price ,OTM put shift 2
                if subminCnt == 2 and int(self.priceVol.get()) == 0:
                    # two price the same,judge is the min
                    if doublePriceValueSub - submidprice.index(min(submidprice)) == 1:
                        outSec = True

            midpox *= 2
            putpox = (putpox *2) +1

            # shift to get
            # call in -2 ,-4.... out +2,+4
            if self.tm.get() == "ITM":
                midpox -= int(self.priceVol.get()) * 2
                putpox += int(self.priceVol.get()) * 2

                if self.atmWay.get() == 'plusAtm':
                    if addminCnt == 2 and int(self.priceVol.get()) != 0:
                        putpox += 2
                else:
                    if subminCnt == 2 and int(self.priceVol.get()) != 0:
                        putpox += 2
            else:
                midpox += int(self.priceVol.get()) * 2
                putpox -= int(self.priceVol.get()) * 2

                if self.atmWay.get() == 'plusAtm':
                    if addminCnt == 2 and int(self.priceVol.get()) != 0:
                        midpox += 2
                else:
                    if subminCnt == 2 and int(self.priceVol.get()) != 0:
                        midpox += 2

            #out put data
            getpo = len(semifinaldata)
            if midpox > getpo or midpox < 0:
                continue

            #not mention begin, so ~~ ha ha
            if self.interval.get() == "point":
                # get callrawdata and putrawdata
                call, put = self.create_atm_form(semifinaldata)
                # add and sub call and put
                plusprice, subprice = self.calculate_atm(call, put)
                # decide callAtm and putAtm
                callidx, putidx = self.atm_decide(plusprice, subprice)
                # poick idx of call and put
                calldataidx, putdataidx = self.atm_shift(callidx, putidx, call, put)
                midpox = calldataidx*2
                putpox = putdataidx*2

            data = semifinaldata[midpox]
            data2 = None
            # if has sec data
            if outSec:
                data2 = semifinaldata[midpox+2]

            print "call " + str(data)


            print n
            print putpox
            print len(semifinaldata)

            if putpox > getpo or putpox < 0:
                continue
            putdata = semifinaldata[putpox]
            putSecdata = None;
            if outSec :
                putSecdata = semifinaldata[putpox+2]
            print "put " + str(putdata)


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

            findata.append(putdata[3])
            findata.append(putdata[5])
            findata.append(putdata[6])
            findata.append(putdata[7])
            findata.append(putdata[8])

            print findata

            findata2 = []
            if outSec:
                findata2.append(data2[0])
                findata2.append(weekday)
                findata2.append(data2[3])
                findata2.append(data2[5])
                findata2.append(data2[6])
                findata2.append(data2[7])
                findata2.append(data2[8])

                findata2.append(putSecdata[3])
                findata2.append(putSecdata[5])
                findata2.append(putSecdata[6])
                findata2.append(putSecdata[7])
                findata2.append(putSecdata[8])

            if outSec:
                dds = ",".join(findata2)
                dds += "\r\n"
                finalds.append(dds)

            ds = ",".join(findata)
            ds +="\r\n"
            finalds.append(ds)

        if len(finalds) == 0:
            self.errorMsg("no match data ,not out put file")
            return

        finalfileName = "week" + "_" + self.tm.get() + "_" + self.atmWay.get() + "_" + self.priceVol.get()
        fp = open(".\\" + finalfileName + ".txt", "wb")
        finalds.reverse()
        for item in finalds:
            fp.write(item)

        fp.close()



    def saveFile(self):

        for dateinfo in self.genDays:
            rdateStart = str(dateinfo.year) + '/' + '{:02d}'.format(dateinfo.month) + "/" + '{:02d}'.format(dateinfo.day)
            rdateEnd = str(dateinfo.year) + '/' + '{:02d}'.format(dateinfo.month) + "/" + '{:02d}'.format(dateinfo.day)
            #my_data = {'DATA_DATE': rdateStart, 'DATA_DATE1': rdateEnd, 'datestart': rdateStart, 'dateend': rdateEnd,'COMMODITY_ID': 'TXO', 'his_year': '2017'}
            my_data = {'queryStartDate': rdateStart, 'queryEndDate': rdateEnd, 'down_type': 1, 'commodity_id': 'TXO'}
            #print my_data
            #r = requests.post('http://www.taifex.com.tw/chinese/3/3_2_3_b.asp', data=my_data)
            r = requests.post('http://www.taifex.com.tw/cht/3/optDataDown.asp', data=my_data)
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
        if len(str) == 175:
            return True
        return False

        matchObj = re.match('(.+)', str)
        # print matchObj.endpos
        if matchObj.endpos == 441:
            return True
        return False

    def filterw4(self,data):

        hasw4 = False
        w4Cnt = 0;
        for row in data:
            # print row[2]
            wjudge = re.compile("(\\d\\d\\d\\d\\d\\d)(W(\\d))*")
            prematchObj = wjudge.match(row[2])
            #check is have w4
            if prematchObj != None and prematchObj.group(2) != None:
                if prematchObj.group(3) == "4":
                    hasw4 = True
                    w4Cnt +=1

        if hasw4 and (w4Cnt == len(data)):
            return data

        newW3 = [];
        if hasw4:
            #filter W4 ,keep data like 201801
            for row in data:
                # print row[2]
                wjudge = re.compile("(\\d\\d\\d\\d\\d\\d)(W(\\d))*")
                prematchObj = wjudge.match(row[2])
                # check is have w4
                if prematchObj != None and prematchObj.group(2) == None:
                    if row[17] == '\xa4@\xaf\xeb':
                        newW3.append(row)
            return newW3
        return data

    def adjustWiredmidprice(self,midprice,pluslist,sublist,type):
        mid = midprice.index(min(midprice))

        #check mid is same as wired,if yes ,find secd min as midprice
        cmp = 100000
        wirdidx = -1
        for i in range(0 ,len(pluslist)):
            price = pluslist[i]
            if (cmp - price) < 0:
                wirdidx = i
                break
            cmp = price
        #no wired , used default mid
        if wirdidx == -1:
            return mid
        elif mid == wirdidx-1:
            wirdidx -= 1
            pluslist[wirdidx] = 99999
            #re plus and find min
            sum = []
            add = 0;
            for i in range(0, len(pluslist)):
                if type ==0:
                    add = pluslist[i] + sublist[i]
                else:
                    add = abs( pluslist[i] - sublist[i])
                sum.append(add)
            return  sum.index(min(sum))

        #find last ,used default
        return mid

    def settledays(self):
        year, month, mydate = self.datepare(self.databegin.get())
        eyear, emonth, emydate = self.datepare(self.dataend.get())
        #month = 10
        #emonth =10
        my_data = {'syear': year, 'smonth': '{:02d}'.format(month), 'eyear': eyear, 'emonth': '{:02d}'.format(emonth),
                   'COMMODITY_ID': 1}
        # print my_data
        r = requests.post('http://www.taifex.com.tw/chinese/5/FutIndxFSP.asp', data=my_data)
        self.stateS.set("grab data ")
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table', {'class': 'table_c'})

        if table is None:
            self.errorMsg("grab settle error!! website may change")
            return None

        for i, tr in enumerate(table.findAll('tr')):
            if i == 0:
                tr.extract()

        table_tr = table.findAll("tr")
        filterdata = []
        if len(table_tr) == 0:
            return filterdata
        else:
            for row in table.findAll("tr"):
                cells = row.findAll("td")
                #print cells[0].find(text=True)
                filterdata.append(cells[0].find(text=True))

        ds = ",".join(filterdata)
        ds += "\r\n"

        # save file
        fp = open(".\\data\\settle.txt", "wb")
        fp.write(ds)
        fp.close()
        return filterdata

    def settlefilter(self):
        if self.settleday.get() == 0:
            return

        #filterdate = self.settledays()
        filterdate = self.grabNewsettledays()


        #if filterdate == None, want settle day and settle day can't grab, not handle
        if filterdate is None:
            return

        newfilter = []
        for dateinfo in self.grabDays:
            # day filter
            today = str(dateinfo.year) + '/' + '{:02d}'.format(dateinfo.month) + "/" + '{:02d}'.format(dateinfo.day)
            if today in  filterdate:
                newfilter.append(dateinfo)

        print newfilter
        if len(newfilter) != 0:
            self.grabDays = newfilter

    def grabNewsettledays(self):
        year, month, mydate = self.datepare(self.databegin.get())
        eyear, emonth, emydate = self.datepare(self.dataend.get())
        my_data = {'start_year': year, 'start_month': '{:02d}'.format(month), 'end_year': eyear, 'end_month': '{:02d}'.format(emonth),'dlFileType':3}
        r = requests.post('https://www.taifex.com.tw/cht/5/fSPDataDown.asp', data=my_data)

        #print r.status_code
        #print len(r.content)
        if len(r.content) == 92:
            #using local settleday.txt
            if os.path.isfile(".\\data\\settleday.txt") == False:
                self.errorMsg("grab settle error!! website may change")
                return None

            #local settleday exsit, read and return
            fd = []
            finfd = [];
            path = ".\\data\\settleday.txt"
            with open(path) as f:
                for line in f:
                    fd = line.strip().split(',')
                    for day in fd:
                        finfd.append(day)
            return finfd

        fp = open(".\\data\\settle.txt", "wb")
        fp.write(r.content)
        fp.close()

        filterdata = []
        path = ".\\data\\settle.txt"
        f = open(path, 'rb')
        for row in csv.reader(f):
            if row[2] == 'TXO':
                filterdata.append(row[0])

        ds = ",".join(filterdata)
        ds += "\r\n"

        # save file
        fp = open(".\\data\\settleday.txt", "wb")
        fp.write(ds)
        fp.close()
        return filterdata

    def create_atm_form(self,rawdata):
        n = len(rawdata)
        calldata = []
        putdata = []
        for i in range(0, n, 2):
            call = rawdata[i]
            putd = rawdata[i + 1]
            calldata.append(call)
            putdata.append(putd)
        return calldata,putdata

    def calculate_atm(self, callrawdata, putrawdata):
        n = len(callrawdata)

        plusmidprice = []
        submidprice = []
        for i in range(0, n):
            calldata = callrawdata[i]
            putdata = putrawdata[i]
            callprice = 0
            putprice = 0
            if calldata[5] == '-':
                callprice = 99999
            else:
                callprice = float(calldata[5])

            if putdata[5] == '-':
                putprice = 99999
            else:
                putprice = float(putdata[5])

            add = callprice + putprice
            plusmidprice.append(add)

            # when using sub condition, call - and put - will be zero, cause judge error, so fix it
            if callprice == 99999 and putprice == 99999:
                sub = 99999
            else:
                sub = abs(callprice - putprice)
            submidprice.append(sub)
        return plusmidprice,submidprice

    def atm_decide(self, callprice,putprice):
        return callprice.index(min(callprice)) ,putprice.index(min(putprice))

    def atm_shift(self,callmid,putmid,callraw,putraw):
        midpox = 0
        putpox = 0

        if self.atmWay.get() == 'plusAtm':
            midpox = callmid
            putpox = callmid
        else:
            midpox = putmid
            putpox = putmid

        if self.interval.get() == "interval":
            if self.tm.get() == "ITM":
                midpox -= int(self.priceVol.get()) * 1
                putpox += int(self.priceVol.get()) * 1
                #to do ,double Atm
            else:
                midpox += int(self.priceVol.get()) * 1
                putpox -= int(self.priceVol.get()) * 1
                # to do ,double Atm
        else:
            #find closest self.pointInterval from Atm
            if self.tm.get() == "ITM":
                target = int(float(callraw[midpox][3])) - int(self.pointInterval.get())
                difflist = []
                for i in range(0, midpox+1):
                    difflist.append(abs(float(callraw[i][3]) - target))
                midpox = difflist.index(min(difflist))

                difflist = []
                target = int(float(putraw[putpox][3])) + int(self.pointInterval.get())
                n = len(putraw)
                for i in range(putpox, n):
                    difflist.append(abs(float(putraw[i][3]) - target))
                putpox += difflist.index(min(difflist))
            else:
                target = int(float(callraw[midpox][3])) + int(self.pointInterval.get())
                difflist = []
                for i in range(0, midpox + 1):
                    difflist.append(abs(float(callraw[i][3]) - target))
                midpox = difflist.index(min(difflist))

                difflist = []
                target = int(float(putraw[putpox][3])) - int(self.pointInterval.get())
                n = len(putraw)
                for i in range(putpox, n):
                    difflist.append(abs(float(putraw[i][3]) - target))
                putpox += difflist.index(min(difflist))
        return midpox,putpox


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


