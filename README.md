# TaxHistory
Tao history sheet gereation

#exe build
c:\Python27\Scripts\pyinstaller.exe -F -w .\main.py

--------------------------------------
-history web
http://www.taifex.com.tw/chinese/3/3_2_3_b.asp?DATA_DATE=2018/08/29&DATA_DATE1=2018/08/29&datestart=2018/08/29&dateend=2018/08/29&COMMODITY_ID=TXO&his_year=2017

-settle web
http://www.taifex.com.tw/chinese/5/FutIndxFSP.asp?syear=2018&smonth=09&eyear=2018&emonth=12&COMMODITY_ID=1
--------------------------------------

------------------------------------
#2018/11/11 source web para modity

fix doubleprice not min bug & doubleprice not continue handle as single data

------------------------------------
#2018/10/03 source web para modity

-history web mofity to 
http://www.taifex.com.tw/cht/3/optDataDown.asp?down_type=1&commodity_id=TXO&queryStartDate=2018/09/04&queryEndDate=2018/10/01

-settle web mofity from web to csv
https://www.taifex.com.tw/cht/5/fSPDataDown.asp?start_year=2017&start_month=01&end_year=2018&end_month=10&dlFileType=3
------------------------------------

