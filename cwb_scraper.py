# coding: utf-8
def cwb_scraper():
    # coding: utf-8
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    import requests
    import datetime
    import string
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

    
    pd.set_option('display.float_format',lambda x : '%.2f' % x)
    
    logging.basicConfig(level=logging.INFO,format='%(levelname)s-[%(asctime)s]-%(message)s',datefmt='%Y-%m-%d %H:%M:%S',filename='scrapLog.log', filemode='a')
    logging.info("new cwb_scraper process")
    
    id = []
    num = []
    maxInt = []
    date = []
    loc = []
    lat = []
    long = []
    depth = []
    mag = []
    link = []

    options = Options()
    options.add_argument('--headless')
    options.add_argument("--start-maximized")
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    url = 'https://www.cwb.gov.tw/V8/E/E/index.html'
    
    run=True

    try:    
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        soup = BeautifulSoup(driver.page_source,'lxml')

        titles = soup.find('tbody',{'class':'eq_list'}).find_all('tr',{'class':'eq-row'})

        year = str(datetime.datetime.now().year)

        link_old = pd.read_csv('cwb_scraper.csv', index_col=0)['Link'].tolist()
        
        for title in titles:
            if('https://www.cwb.gov.tw' + title.find('a').get('href')) not in link_old: 
                link.append('https://www.cwb.gov.tw' + title.find('a').get('href')) 
                    
                num.append(title.find('td',{'headers':'num'}).text)
                    
                maxInt.append(title.find('td',{'headers':'maximum'}).text)
                    
                eq_detail = title.find(class_="eq-detail")
                eq_lis  =eq_detail.find_all('li')
                    
                loc.append(eq_lis[0].text.split('Location')[1])
                depth.append(eq_lis[1].contents[1].split('km')[0])
                mag.append(eq_lis[2].contents[1])
                    
                #details
                driver2 = webdriver.Chrome(options=options)
                driver2.get("https://www.cwb.gov.tw" + title.find('a').get('href'))
                    
                soup = BeautifulSoup(driver2.page_source,'lxml')
                    
                titles2 = soup.find('ul',{'class':'list-unstyled quake_info'})
                lis = titles2.find_all('li')
                    
                date.append(lis[0].text.split('Origin Time: ')[1].replace("/","-"))
                lat.append(lis[1].text.split('Epicenter: ')[1].split('°N')[0])
                long.append(lis[1].text.split('°E')[0].split(',')[1])
                    
                string_punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '
                translator = str.maketrans('', '', string_punctuation)
                id= [s.translate(translator) for s in date]
                    
                driver2.quit()
                
        driver.quit()
        
    except Exception as e:
        logging.info(str(e)+',process end')
        run=False    
        
    if run:     
        table ={
            "ID":id,
            "Number":num,
            "LargestIntensity":maxInt,
            "Origin Time":date,
            "Location":loc,
            "Latitude":lat,
            "longtitude":long,
            "Depth":depth,
            "Magnitude":mag,
            "Link":link
            }

        df_old = pd.read_csv('cwb_scraper.csv',index_col=0,dtype={"Link":'object'})
        df_new = pd.DataFrame(table)

        df_append = df_new.append(df_old, ignore_index=True).drop_duplicates('Link')
        df_append =df_append.astype({"Link": 'object'})
        
        if df_append.equals(df_old):
            logging.info('no new event exist,process end')
            
        else:
            df_append.to_csv('cwb_scraper.csv', encoding = 'utf_8_sig')
            logging.info(str(len(link))+'new event exist,cwb_scraper.csv append')
            df_new=df_append.append(df_old, ignore_index=True).drop_duplicates('Link',keep=False)
            new_events=df_new['ID'].tolist()
            
            #ftp start
            try:
                ftp = ftpEvent.ftpLogin()

                ftpEvent.ftpEvents(ftp,new_events)

                logging.info('process end')
            except Exception as e:
                logging.error(e)
        mFileList.allFileListCsv()
    return run

cwb_scraper()  
