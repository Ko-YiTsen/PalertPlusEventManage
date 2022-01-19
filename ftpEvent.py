# coding: utf-8
from ftplib import FTP
import logging
import os
import datetime
import time
# 外部函式
import waveform
import mFileList
import ftpInfo

path = os.getcwd()
# ftp改參數
ftpInfo = {
    'IP': '140.115.78.115',
    'port': 12121,
    'account': 'palertRead',
    'password': '401r401r'
}

# ftp start


class SmartFTP(FTP):
    def makepasv(self):
        invalidhost, port = super(SmartFTP, self).makepasv()
        return self.host, port

# 登入
# ftp = ftpEvent.ftpLogin()


def ftpLogin():

    ftp = SmartFTP(ftpInfo['IP'])

    ftp.connect(ftpInfo['IP'], ftpInfo['port'], 30)
    ftp.login(ftpInfo['account'], ftpInfo['password'])
    return ftp

# 下載多個檔案


def ftpEvents(ftp, eventList, start=-20, end=90):
    flist = ftp.nlst()

    # ------------

    for event in eventList:

        # trans to utc
        # 設定時間在-20~1:30
        t_event = datetime.datetime.strptime(
            str(event)[:14], '%Y%m%d%H%M%S')-datetime.timedelta(hours=8, seconds=-start)

        t_twomin = t_event+datetime.timedelta(seconds=end-start)
        t_event = int(t_event.strftime('%Y%m%d%H%M%S'))
        t_twomin = int(t_twomin.strftime('%Y%m%d%H%M%S'))
        logging.info('ftp start '+str(event))

        for file in flist:
        
            #download .mseed file       
            if 'mseed' in file:
                ftime = int(file[:14])
                if (int(ftime) > int(t_event)) & (file[20] != '4') & (int(ftime) < int(t_twomin)):
                    logging.info('download ' + file)
                    # open the file to save ftpfile
                    filePath = path+'/eqdata/' + \
                        str(event)+'/' + \
                        'allFile' + '/' + \
                        file.replace('[', '_').replace(']', '')
                    download = open(filePath, 'wb')

                    count = 0  # attempt time count
                    while count < 8:
                        try:
                            # download file from ftp
                            ftp.retrbinary('RETR ' + file, download.write)

                            # os.rename(file,file.replace('[','_').replace(']','_'))
                            # newFileBytes=[123,3,255,0,100]
                            # int_bytes = bytearray(newFileBytes)
                            # download.write(int_bytes)
                            if count > 0:
                                logging.info('success '+file)
                            count = 10
                        except Exception as e:
                            count += 1
                            logging.error(str(e)+' retry'+str(count))
                    if count == 8:
                        logging.error('pass '+file)
                    download.close()
                    waveform.plot_waveform(filePath)
                           
                    download.close()
                    
            #download .csv file
            if 'palert' in file:
                ftime = datetime.datetime.strptime(
                file[21:].split('.')[0], '%Y%m%d%H%M%S')-datetime.timedelta(hours=8)
                filetime =int(ftime.strftime('%Y%m%d%H%M%S'))
                if (filetime > int(t_event)) & (filetime < int(t_twomin)):
                    logging.info('download ' + file)
                    filePath = path+'/eqdata/' + \
                        str(event)+'/' + \
                        'allFile' + '/' + \
                        str(file)
                    print(filePath)
                    download = open(filePath, 'wb')
                    
                    count = 0  # attempt time count
                    while count < 8:
                        try:
                            # download file from ftp
                            ftp.retrbinary('RETR ' + file, download.write)
                            if count > 0:
                                logging.info('success '+file)
                            count = 10
                        except Exception as e:
                            count += 1
                            logging.error(str(e)+' retry'+str(count))
                    if count == 8:
                        logging.error('pass '+file)
                           
                    download.close()        
                    
        # print(t_twomin)
    ftp.quit()
    logging.info('ftp done')

#只下載一個事件的檔案  重抓用
def ftpEvent(ftp, event, start:int, end:int):
    text=[]
    flist = ftp.nlst()
    t_event = datetime.datetime.strptime(
        str(event), '%Y%m%d%H%M%S')-datetime.timedelta(hours=8, seconds=-(start))

    t_twomin = t_event+datetime.timedelta(seconds=end-start)
    t_event = int(t_event.strftime('%Y%m%d%H%M%S'))
    t_twomin = int(t_twomin.strftime('%Y%m%d%H%M%S'))
    logging.info('ftp start '+str(event))
    text.append('ftp start '+str(event))
    for file in flist:
            if 'mseed' in file:
                ftime = int(file[:14])

                if (int(ftime) > int(t_event)) & (file[20] != '4') & (int(ftime) < int(t_twomin)):
                    logging.info('download ' + file)
                    text.append('download ' + file)
                    # open the file to save ftpfile
                    filePath = path+'/eqdata/' + \
                        str(event)+'/' + \
                        file.replace('[', '_').replace(']', '')
                    download = open(filePath, 'wb')

                    count = 0  # attempt time count
                    while count < 5:
                        try:
                            # download file from ftp
                            ftp.retrbinary('RETR ' + file, download.write)

                            # os.rename(file,file.replace('[','_').replace(']','_'))
                            # newFileBytes=[123,3,255,0,100]
                            # int_bytes = bytearray(newFileBytes)
                            # download.write(int_bytes)
                            if count > 0:
                                logging.info('success '+file)
                                text.append('success '+file)
                            count = 10
                        except Exception as e:
                            count += 1
                            logging.error(str(e)+' retry'+str(count))
                            text.append('ERROR: '+str(e)+' retry'+str(count))
                    if count == 5:
                        logging.error('pass '+file)
                        text.append('pass '+file)
                    download.close()
                    waveform.plot_waveform(filePath)

        # print(t_twomin)
    ftp.quit()
    logging.info('ftp done')
    text.append('ftp done')
    return text
