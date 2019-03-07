import os
from Tkinter import *
import datetime
import time
import re
import requests
from datetime import date
from collections import OrderedDict
import collections
import csv
from bs4 import BeautifulSoup
from StringIO import StringIO

from DB.db_proxy import *
db = db_proxy()

class Application(Frame):

    def createWidgets(self):

        group = LabelFrame(self, text="time", padx=5, pady=5)
        group.pack(padx=5, pady=5)

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

        ig = LabelFrame(self, text="ITM OTM", padx=5, pady=5)
        ig.pack(side=LEFT,padx=10, pady=10)
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

        ag = LabelFrame(self, text="OP or CP", padx=5, pady=5)
        ag.pack(side=LEFT, padx=10, pady=10)
        MODES = [
            ("OpenPrice", "OpenPrice"),
            ("ClosePrice", "ClosePrice"),
        ]
        self.OPorCP = StringVar()
        self.OPorCP.set("OpenPrice")  # initialize

        for text, mode in MODES:
            b = Radiobutton(ag, text=text,
                            variable=self.OPorCP, value=mode)
            b.pack(anchor=W)

        gb = LabelFrame(self, text="Atm(plus or sub)", padx=5, pady=5)
        gb.pack(side=LEFT,padx=10, pady=10)

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

        self.pickorder = IntVar()
        d = Checkbutton(gSett, text="pick openning transaction", variable=self.pickorder)
        d.pack()

        Sett = LabelFrame(self, text="outRawData", padx=5, pady=5)
        Sett.pack(padx=10, pady=10)
        self.rawDataout = IntVar()
        self.rawDataout.set(1)
        e = Checkbutton(Sett, text="rawData", variable=self.rawDataout)
        e.pack()


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
        year, month, mydate = self.datepare(self.databegin.get())
        eyear, emonth, emydate = self.datepare(self.dataend.get())

        #month check
        if self.dateinputCheck(month, mydate) == FALSE:
            return
        if self.dateinputCheck(emonth, emydate) == FALSE:
            return

        nowday = date(year, month, mydate)
        backday = date(eyear, emonth, emydate)

        totalday = -(nowday-backday).days+1

        # count for now day
        self.state = 0
        oneday = datetime.timedelta(days=1)
        self.grabDays = []#OrderedDict()
        alldaymaker = []
        firstday = ''
        lastday = ''
        # if check settle
        if self.settleday.get() == 0:
            for num in range(0, totalday):
                delta = datetime.timedelta(days=num)
                newday = backday - delta
                datemaker = str(newday.year) + "\\" + '{:02d}'.format(newday.month) + "\\" + '{:02d}'.format(newday.day)
                alldaymaker.append(datemaker)
                if num == 0:
                    lastday = datemaker
                if num == totalday-1:
                    firstday = datemaker
                self.grabDays.append(datemaker)
            #self.grabDays = collections.OrderedDict(reversed(list(self.grabDays.items())))
            alldaymaker.reverse()
            #check db querydatelist
            grabday = db.get("option/querydate")
            dbgrabday = grabday.get()
            if dbgrabday == None:
                #create datelist
                dayrange = dict()
                dayrange['firstday'] = firstday
                dayrange['lastday'] = lastday
                db.save("option/querydate/datelist", dayrange)

        else:
            if self.settlefilter():
                self.errorMsg("settle day error occurred!! no match settle data")
                return

            firstday =  self.grabDays[0]
            lastday =  self.grabDays[-1]

        #print len(self.grabDays)
        #save file
        self.stateS.set("start = grab data....")
        self.saveFile(firstday,lastday)
        self.stateS.set("start = grab data ok")

        if self.state ==1:
            return

        #load db data
        self.loadcsv(firstday,lastday)

    def loadcsv(self,firstday,endday):

        stopdayname = '0'
        finalfileName = ""
        finalds = []
        settleRawData = []

        grabday = db.get("option/data")
        #dbgrabday = grabday.order_by_key().get()
        #firstday, endday = self.getdateRange()
        dbgrabday = grabday.order_by_key().start_at(firstday).end_at(endday).get()

        n = len(dbgrabday)

        if n == 0:
            self.errorMsg("no match data ,output empty file")
            return

        call = []
        put = []
        part1Call = []
        part1Put = []
        weekday =''
        midpox = 0
        putpox = 0
        for data,value in dbgrabday.items():
            if self.settleday.get() == 1:
                #exculsive normal day
                if data not in self.grabDays:
                    continue
            arr = data.split('\\')
            weekday = datetime.datetime(int(arr[0]),int(arr[1]),int(arr[2])).strftime("%w")
            if self.settleday.get() and self.pickorder.get():
                call = value["part2"]['call'].split('#')
                put = value["part2"]['put'].split('#')
                #part1 extral saving
                part1Call = [str(i) for i in value["part1"]['call'].split('#')]
                part1Put = [str(i) for i in value["part1"]['put'].split('#')]
            else:
                call = [str(i) for i in value["part1"]['call'].split('#')]
                put = [str(i) for i in value["part1"]['put'].split('#')]

            #check un-normal decline (like 2016/5/5 wired , 288-> 104-> 196)
            midpox = 0
            putpox = 0
            #not mention begin, so ~~ ha ha
            addPriceCnt = 0
            subPriceCnt2 = 0

            # get callrawdata and putrawdata
            #call, put = self.create_atm_form(semifinaldata)
            # add and sub call and put
            plusprice, subprice = self.calculate_atm(call, put)
            # decide callAtm and putAtm
            print  plusprice
            print  subprice
            callidx, putidx = self.atm_decide(plusprice, subprice)
            addPriceCnt, subPriceCnt2 = self.doublie_InThePriceCehck(plusprice, subprice)
            # poick idx of call and put
            print  callidx
            print  putidx
            calldataidx, putdataidx = self.atm_shift(callidx, putidx, call, put,addPriceCnt,subPriceCnt2)

            midpox = calldataidx
            putpox = putdataidx

            if weekday == "0":
                weekday = "7"
            findata = self.ouputFun(call[midpox],put[putpox],weekday)

            ds = ",".join(findata)
            ds +="\r\n"
            finalds.append(ds)

            if addPriceCnt == 2 and self.atmWay.get() == 'plusAtm':
                if int(self.priceVol.get()) == 0:
                    second = self.ouputFun(call[midpox+1], put[putpox+1], weekday)
                    ds = ",".join(second)
                    ds += "\r\n"
                    finalds.append(ds)
            if subPriceCnt2 == 2 and self.atmWay.get() == 'subAtm':
                if int(self.priceVol.get()) == 0:
                    second = self.ouputFun(call[midpox + 1], put[putpox + 1], weekday)
                    ds = ",".join(second)
                    ds += "\r\n"
                    finalds.append(ds)

            # settle data save ,pick and merge later
            if self.settleday.get() and self.pickorder.get():
                settleRawData.append([part1Call,part1Put,weekday,findata[2],findata[9]])


        if len(finalds) == 0:
            self.errorMsg("no match data ,not out put file")
            return

        #mereg pick settle
        merge = []
        if self.settleday.get() and self.pickorder.get():
            merge.append(finalds.pop(0))
            settlePart = self.settlePick(settleRawData)
            n = len(settlePart)

            for i in range(0,n):
                merge.append(settlePart[i])
                merge.append(finalds[i])

            merge
        else:
            merge = finalds

        finalfileName = "week" + "_" + self.tm.get() + "_" + self.atmWay.get() + "_" + self.priceVol.get()

        if self.interval.get() == "point":
            finalfileName += "_" + self.pointInterval.get()
        fp = open(".\\" + finalfileName + ".txt", "wb")

        for item in merge:
            fp.write(item)

        fp.close()

        if self.rawDataout.get():
            self.OutputrawData(call,put)


    def ouputFun(self,calldata,putdata,weekday):
        data = calldata.split(',')
        print "call " + str(data)
        putdata = putdata.split(',')
        print "put " + str(putdata)

        findata = []

        findata.append(data[0])
        findata.append(weekday)
        findata.append(str(int(float(data[3]))))
        findata.append(data[4])
        findata.append(data[5])
        findata.append(data[6])
        findata.append(data[7])
        findata.append(data[13])
        findata.append(data[14])

        findata.append(str(int(float(putdata[3]))))
        findata.append(putdata[4])
        findata.append(putdata[5])
        findata.append(putdata[6])
        findata.append(putdata[7])
        findata.append(putdata[13])
        findata.append(putdata[14])

        return  findata

    def filterExcusivePart(self,allpart,pickpart):
        n = len(pickpart)
        for i in range(0,n):
            re = allpart.index(pickpart[i])
            allpart.remove(allpart[re])

        return  allpart

    def settlePartdata(self,settledata,weekday):
        if self.interval.get() == "point":
            # get callrawdata and putrawdata
            call, put = self.create_atm_form(settledata)
            # add and sub call and put
            plusprice, subprice = self.calculate_atm(call, put)
            # decide callAtm and putAtm
            callidx, putidx = self.atm_decide(plusprice, subprice)
            # poick idx of call and put
            calldataidx, putdataidx = self.atm_shift(callidx, putidx, call, put,0,0)
            midpox = calldataidx * 2
            putpox = putdataidx * 2 + 1

        data = settledata[midpox]
        print "call " + str(data)

        putdata = settledata[putpox]
        print "put " + str(putdata)

        if weekday == "0":
            weekday = "7"

        findata = []
        findata.append(data[0])
        findata.append(weekday)
        findata.append(data[3])
        findata.append(data[5])
        findata.append(data[6])
        findata.append(data[7])
        findata.append(data[8])
        findata.append(data[14])
        findata.append(data[15])

        findata.append(putdata[3])
        findata.append(putdata[5])
        findata.append(putdata[6])
        findata.append(putdata[7])
        findata.append(putdata[8])
        findata.append(putdata[14])
        findata.append(putdata[15])

        return findata

    def settlePick(self,RawSettle):
        n = len(RawSettle)
        finalds = []
        for i in range(0,n-1):
            raw = RawSettle[i]
            findata3 = self.settlePickSamePrice(RawSettle[i+1][0],RawSettle[i+1][1], raw[2], raw[3], raw[4])
            dds = ",".join(findata3)
            dds += "\r\n"
            finalds.append(dds)
        return finalds

    def settlePickSamePrice(self,part1call,part1put,weekday,callPrice,putPrice):

        n = len(part1call)
        calldataidx =0
        for i in range(0,n):
            call = part1call[i].split(',')
            num = int(float(call[3]))
            if int(float(callPrice)) == num:
                calldataidx =i
                break

        n = len(part1put)
        putdataidx = 0
        for i in range(0,n):
            put = part1put[i].split(',')
            num = int(float(put[3]))
            if int(float(putPrice)) == num:
                putdataidx =i
                break

        midpox = calldataidx
        putpox = putdataidx

        data = part1call[midpox]
        putdata = part1put[putpox]

        if weekday == "0":
            weekday = "7"

        findata = self.ouputFun(data,putdata,weekday)
        return findata


    def saveFile(self,firstday,lastday):

        grabday = db.get("option/querydate")
        dbgrabday = grabday.get()
        dbdayRange = dbgrabday['datelist']
        firstlimit = self.day1bigDay2Compare(firstday,dbdayRange['firstday'])
        lastlimit = self.day1SmallDay2Compare(lastday, dbdayRange['lastday'])

        #dayrange in dbrange,data already in db,pass for next function to query
        if firstlimit and lastlimit:
            return

        #update db data
        grabday = db.get("option/data")
        dbgrabday = grabday.order_by_key().get()

        anyupdate = False
        for date in self.grabDays:
            if dbgrabday != None:
                if date in dbgrabday:
                    continue

            rdateStart = date.replace("\\", "/")
            rdateEnd = date.replace("\\", "/")
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

            #print r.content
            #f = StringIO(r.content)
            reader = csv.reader(r.content.split('\n'), delimiter=',')
            i = 0
            lastprice =0
            nextprice = 0
            set1 = []
            set2 = []
            putin = 0
            putCnt = 0

            for row in reader:
                if i == 0:
                    i = 1
                    continue
                if i == 1:
                    i = 2
                    lastprice = int(float(row[3]))
                nextprice =  int(float(row[3]))

                #replse new price
                if nextprice > lastprice:
                    lastprice = nextprice
                elif nextprice < lastprice:
                    lastprice = nextprice
                    if putCnt == 0:
                        putin = 1
                        # read second section
                        putCnt = 1
                    else:
                        break;

                if putin ==0:
                    if row[17] == '\xa4@\xaf\xeb':
                        del row[17]
                        del row[4]
                        set1.append(row)
                else:
                    if row[17] == '\xa4@\xaf\xeb':
                        del row[17]
                        del row[4]
                        set2.append(row)

            #sepreate to 2 part
            rdateStart = rdateStart.replace("/", "\\")

            call = []
            put = []
            for i,item in enumerate(set1):
                cell = ','.join(item)
                if i % 2 ==0:
                    call.append(cell)
                else:
                    put.append(cell)
            part = dict()
            part['call'] = '#'.join(map(str, call))
            part['put'] = '#'.join(map(str, put))

            call_1 =[]
            put_1 = []
            for i,item in enumerate(set2):
                cell = ','.join(item)
                if i % 2 ==0:
                    call_1.append(cell)
                else:
                    put_1.append(cell)
            part2 = dict()
            part2['call'] = '#'.join(map(str, call_1))
            part2['put'] = '#'.join(map(str, put_1))

            dd = dict()
            dd['part1'] = part
            dd['part2'] = part2

            db.save("option/data/" + rdateStart, dd)
            anyupdate = True

        # over range ,update new range
        #re write first day
        if firstlimit == False:
            dbdayRange['firstday'] = firstday
        if lastlimit == False:
            if anyupdate:
                dbdayRange['lastday'] = lastday
        db.save("option/querydate/datelist",dbdayRange)


    def nodata(self, str):
        if len(str) == 175:
            return True
        return False

        matchObj = re.match('(.+)', str)
        # print matchObj.endpos
        if matchObj.endpos == 441:
            return True
        return False


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

    def day1SmallDay2Compare(self,day1,day2):
        date1 = "2015/12/31"
        date2 = "2015/12/31"
        newdate1 = time.strptime(day1, "%Y\%m\%d")
        newdate2 = time.strptime(day2, "%Y\%m\%d")

        return newdate1 <= newdate2

    def day1bigDay2Compare(self, day1, day2):
        date1 = "2015/12/31"
        date2 = "2015/12/31"
        newdate1 = time.strptime(day1, "%Y\%m\%d")
        newdate2 = time.strptime(day2, "%Y\%m\%d")

        return newdate1 >= newdate2

    def settledays(self):
        year, month, mydate = self.datepare(self.databegin.get())
        eyear, emonth, emydate = self.datepare(self.dataend.get())
        my_data = {'_all': "on",'start_year': year, 'start_month': '{:02d}'.format(month), 'end_year': eyear, 'end_month': '{:02d}'.format(emonth),'COMMODITY_ID': 2}
        firstday = str(year)+"\\"+'{:02d}'.format(month)+ "\\" +'{:02d}'.format(mydate)
        endday =  str(eyear) + "\\" + '{:02d}'.format(emonth)  +"\\"+'{:02d}'.format(emydate)

        #check db first
        settleday = db.get("option/settledays/settlehistory")
        settle = settleday.get()
        if settle != None:
            historyday = db.get("option/settledays/settlehistory").get().split(',')
            firstlimit = self.day1bigDay2Compare(firstday,historyday[0])
            lastlimit = self.day1SmallDay2Compare(endday,historyday[-1])

            #in db range just return db info, not ,biger or last , grab again
            if firstlimit and lastlimit:
                settle =  self.getdbsettleday("option/settledays/settlehistory",firstday,endday)
                return settle


        #r = requests.post('http://www.taifex.com.tw/cht/5/FutIndxFSP.asp', data=my_data)
        r = requests.post('https://www.taifex.com.tw/cht/5/optIndxFSP', data=my_data)

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

        if settle == None:
            filterdata.sort()
            datastring = ','.join(filterdata)
            datastring = datastring.replace("/", "\\")
            settle = dict()
            settle['settlehistory'] = datastring
            db.save("option/settledays",settle)
        else:
            #get hisotry settle day
            historyday = db.get("option/settledays/settlehistory").get().split(',')

            # if new settle day not in history ,update it
            for item in filterdata:
                item = item.replace("/", "\\")
                if item not in historyday:
                    historyday.append(item)

            historyday.sort()

            datastring = ','.join(historyday)
            settle = dict()
            settle['settlehistory'] = datastring
            db.save("option/settledays",settle)

        settle =  self.getdbsettleday("option/settledays/settlehistory",firstday,endday) #settleday.order_by_key().start_at(firstday).end_at(endday).get()
        return settle

    def getdbsettleday(self,key,firstday,endday):
        historyday = db.get(key).get().split(',')
        pick = []
        smallthen = filter(lambda day: self.day1SmallDay2Compare(day, endday), historyday)
        rangeday = filter(lambda day: self.day1bigDay2Compare(day, firstday), historyday)
        return  rangeday

    def getdateRange(self):
        year, month, mydate = self.datepare(self.databegin.get())
        eyear, emonth, emydate = self.datepare(self.dataend.get())
        firstday = str(year) + "\\" + '{:02d}'.format(month) + "\\" + '{:02d}'.format(mydate)
        endday = str(eyear) + "\\" + '{:02d}'.format(emonth) + "\\" + '{:02d}'.format(emydate)
        return firstday ,endday

    def settlefilter(self):
        filterdate = self.settledays()
        #filterdate = self.grabNewsettledays()

        # if filterdate == None, want settle day and settle day can't grab, not handle
        if len(filterdate) == 0:
            return 1

        self.grabDays = filterdate
        return 0

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
            calldata = callrawdata[i].split(',')
            putdata = putrawdata[i].split(',')
            callprice = 0
            putprice = 0
            if calldata[self.OpenOrClose()] == '-':
                callprice = 99999
            else:
                callprice = float(calldata[self.OpenOrClose()])

            if putdata[self.OpenOrClose()] == '-':
                putprice = 99999
            else:
                putprice = float(putdata[self.OpenOrClose()])

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
        return  callprice.index(min(callprice)),putprice.index(min(putprice))


    def doublie_InThePriceCehck(self,callprice,putprice):
        intheprice = callprice.index(min(callprice))
        cnt = callprice.count(callprice[intheprice])
        if cnt ==2:
            if callprice[intheprice+1] == callprice[intheprice]:
                cnt = 2
            else:
                cnt =1
        intheprice = putprice.index(min(putprice))
        cnt2 = putprice.count(putprice[intheprice])
        if cnt2 ==2:
            if putprice[intheprice+1] ==  putprice[intheprice]:
                cnt2 = 2
            else:
                cnt2 =1
        return cnt,cnt2


    def atm_shift(self,callmid,putmid,callraw,putraw,addcnt,subcnt2):
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
                print int(self.priceVol.get())
                midpox -= int(self.priceVol.get()) * 1
                putpox += int(self.priceVol.get()) * 1
                if int(self.priceVol.get()) >= 1:
                    if self.atmWay.get() == 'plusAtm':
                        if addcnt >= 2:
                            putpox +=1
                    else:
                        if subcnt2 >= 2:
                            putpox += 1

            else:
                midpox += int(self.priceVol.get()) * 1
                putpox -= int(self.priceVol.get()) * 1
                if int(self.priceVol.get()) >= 1:
                    if self.atmWay.get() == 'plusAtm':
                        if addcnt >= 2:
                            midpox +=1
                    else:
                        if subcnt2 >= 2:
                            midpox += 1
        else:
            #find closest self.pointInterval from Atm
            callraw2 = callraw[midpox].split(',')
            putraw2 = putraw[putpox].split(',')
            if self.tm.get() == "ITM":
                target = int(float(callraw2[3])) - int(self.pointInterval.get())
                pick = 0
                for i in range(0, midpox+1):
                    callraw3 = callraw[i].split(',')
                    if int(float(callraw3[3])) >= target:
                        pick = i
                        break
                midpox = pick

                target = int(float(putraw2[3])) + int(self.pointInterval.get())
                n = len(putraw)
                for i in range(n-1,0,-1):
                    putraw3 = putraw[i].split(',')
                    if int(float(putraw3[3])) <= target:
                        pick = i
                        break
                putpox = pick
            else:
                target = int(float(callraw2[3])) + int(self.pointInterval.get())
                pick = 0
                n = len(callraw)
                for i in range(n-1,0, -1):
                    callraw3 = callraw[i].split(',')
                    if int(float(callraw3[3])) <= target:
                        pick = i
                        break
                midpox = pick

                target = int(float(putraw2[3])) - int(self.pointInterval.get())
                for i in range(0, putpox+1):
                    putraw3 = putraw[i].split(',')
                    if int(float(putraw3[3])) >= target:
                        pick = i
                        break
                putpox = pick

        return midpox,putpox

    def OpenOrClose(self):
        if self.OPorCP.get() == "OpenPrice":
            return 4
        return 7

    def OutputrawData(self,call,put):
        finalds = []

        n = len(call)
        for i in range(0,n):
            findata = []
            calldata = call[i].split(",")
            findata.append(calldata[4])
            findata.append(calldata[5])
            findata.append(calldata[6])
            findata.append(calldata[7])
            findata.append(calldata[13])
            findata.append(calldata[14])
            findata.append(calldata[3])

            putdata = put[i].split(",")
            findata.append(putdata[4])
            findata.append(putdata[5])
            findata.append(putdata[6])
            findata.append(putdata[7])
            findata.append(putdata[13])
            findata.append(putdata[14])

            ds = ",".join(findata)
            ds += "\r\n"
            finalds.append(ds)

        fp = open(".\\" + "rawData" + ".txt", "wb")
        for item in finalds:
            fp.write(item)

        fp.close()


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


