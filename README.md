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
2019/03/07 db migration
--2013/1/11,兩天一樣價平 2013/2/21 2015/12/30
--2013/08/19 不連續價平
--2015/06/05 [99999.4, 99999.4, 100000.2, 100000.9, 299.8, 240.5, 123.0, 173.0, 149.0, 131.0, 133.0, 133.0, 151.0, 168.5, 141.7, 269.5, 331.6, 381.0, 438.6, 492.7, 99999.5, 99999.5, 99999.3, 199998, 199998]
--2016/05/05 中間出現最小,但不是最底波 not fix
--2016/05/05,4,7950,104,257,104,220,257,104,7950,8.9,13,4.2,6.8,13,4.2
  	
\d{4}/(\d{2}|\d{1})/(\d{2}|\d{1}),
-----------------------------------
