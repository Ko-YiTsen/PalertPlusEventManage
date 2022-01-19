# coding: utf-8
def scweb_cwb():
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    import requests
    import datetime
    import time
    import re
    from ftplib import FTP
    import logging

    import os
    import sys
    import pandas as pd
    from pandas._testing import assert_frame_equal

    #外部函式
    import waveform
    import mFileList 
    import ftpEvent

    path = os.getcwd()

    #pd.reset_option('display.float_format')
    pd.set_option('display.float_format',lambda x : '%.2f' % x)

    
    logging.basicConfig(level=logging.INFO,format='%(levelname)s-[%(asctime)s]-%(message)s',datefmt='%Y-%m-%d %H:%M:%S',filename='scrapLog.log', filemode='a')
    logging.info("new scweb_cwb_scraper process")
    
    eq_ID = []
    href = []
    date = []
    num = []
    intens = []
    pos = []
    dep = []
    mag = []

    lat = []
    long = []


    options = Options()
    options.add_argument('--headless')
    options.add_argument("--start-maximized")
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])


    # 氣象局主cwb
    url_1 = 'https://www.cwb.gov.tw/V8/C/E/index.html'
    # 測報中心scweb
    url_2 = 'https://scweb.cwb.gov.tw/zh-tw/earthquake/data'

    run=True
    

    try:
        # 啟動模擬瀏覽器
        driver = webdriver.Chrome(options=options)
        # import time
        

        # 取得網頁代碼
        driver.get(url_2)
        # options.add_argument('--headless')

        # time.sleep(15)

         


        # 指定 lxml 作為解析器
        soup = BeautifulSoup(driver.page_source, features='lxml')
        #soup = BeautifulSoup(ddload,"html.paser")

        tbody = soup.find('tbody')

        # <tbody>内所有<tr>標籤
        trs = tbody.find_all('tr')


        # 使用datetime取得時間年分
        year = str(datetime.datetime.now().year)

        # 先取ID列表去重節省開新網站拿經緯度的時間


        ID_old = pd.read_csv('scweb_cwb_scraper.csv', index_col=0)['ID'].tolist()

        # #對list中的每一項 <tr>
        for tr in trs:
            # ID
            if (int(tr.get('id')[3:17])) not in ID_old:
                
                eq_ID.append((tr.get('id')[3:17]))
                logging.info('scrapping '+tr.get('id')[3:17])

                tds = tr.find_all('td')
                # 編號
                if tds[0].text != '':
                    num.append(tds[0].text[:3])
                else:
                    num.append('000')
                # 震度
                if tds[1].text[1]=="弱":
                    intensity=tds[1].text[0]+("-")
                elif tds[1].text[1]=="強":
                    intensity=tds[1].text[0]+("+")
                else :
                    intensity=tds[1].text[0]
                intens.append(intensity)
                # 規模
                mag.append(float(tds[3].text))
                # 深度
                dep.append(float(tds[4].text))
                # 網址
                href.append("https://scweb.cwb.gov.tw/"+tds[5].find('a').get('href'))
                # 日期
                date.append(tds[6].contents[0])
                # 位置
                pos.append(tds[5].find('a').get('title'))


                # new event dir
                os.makedirs(path+'/eqdata/'+(tr.get('id')[3:17])+'/allFile', exist_ok=True)
                
                #下載報告圖
                if not os.path.isfile(path+'/eqdata/'+(tr.get('id')[3:17])+'/'+(tr.get('id')[3:17])+'.gif'):
                    imgUrl='https://scweb.cwb.gov.tw/webdata/OLDEQ/'+tr.get('id').split('_')[1][:6]+'/'+tr.get('id').split('_')[1]+'.gif'
                    print(imgUrl)
                    r=requests.get(imgUrl)
                    with open(path+'/eqdata/'+(tr.get('id')[3:17])+'/'+(tr.get('id')[3:17])+'.gif','wb') as f:
                    #將圖片下載下來
                        f.write(r.content)



                driver2 = webdriver.Chrome(options=options)
                driver2.get("https://scweb.cwb.gov.tw/"+tds[5].find('a').get('href'))

                soup2 = BeautifulSoup(driver2.page_source, 'lxml')

                titles2 = soup2.find('ul', {'class': 'eqResultBoxRight BulSet BkeyinList'})
                lis = titles2.find_all('li')
                

                lat.append(float(lis[2].contents[3].text.split(' ')[1]))
                long.append(float(lis[2].contents[3].text.split(' ')[4]))
                driver2.quit()
                print(len(lat))

        #   取時間, <tr>內的<th>, <th>內為時間 月/日<br>時:分
            # d = tr.th.text
            # d = year + d
        #   字串轉為datetime格式
            # date.append(datetime.datetime.strptime(d, '%Y%m/%d %H:%M'))


        # 關閉模擬瀏覽器
        driver.quit()
    except Exception as e:
        logging.error(str(e)+',process end')
        run=False

    ################################################################################
    




    if run:
        table = {
            "ID": eq_ID,
            "Number": num,
            "LargestIntensity": intens,
            "Origin Time": date,
            "Location": pos,
            "Latitude": lat,
            "longtitude": long,
            "Depth": dep,
            "Magnitude": mag,
            "Link": href
        }

        df_old = pd.read_csv('scweb_cwb_scraper.csv', index_col=0,dtype={"ID":'object',"Number":'object'})
        df_new = pd.DataFrame(table)


        df_append = df_new.append(df_old, ignore_index=True).drop_duplicates("ID")
        df_append =df_append.astype({"ID": 'object'})
        df_append.sort_values(by=['ID'],ascending=False, ignore_index=True,inplace=True)
        # print(df_append)
        # assert_frame_equal(df_old,df_append)

        if len(eq_ID)==0:
            # no new event
            
            logging.info('no new event exist,process end')
        else:
            # new event
            #df_append.to_csv(( 'url2_' + time.strftime("%Y%m%d-%H%M%S") + '.csv'), encoding = 'utf_8_sig')
            df_append.to_csv('scweb_cwb_scraper.csv', encoding='utf_8_sig')
            logging.info(str(len(eq_ID))+'new event exist,scweb_cwb_scraper.csv append')
            # find out new
            df_new = df_append.append(df_old, ignore_index=True).drop_duplicates("ID", keep=False)
            new_events = df_new['ID'].tolist()

            # ftp start
            
            try:
                ftp = ftpEvent.ftpLogin()

                ftpEvent.ftpEvents(ftp,new_events)

                logging.info('process end')
            except Exception as e:
                logging.error(e)
        mFileList.allFileListCsv()
    return run

scweb_cwb()

