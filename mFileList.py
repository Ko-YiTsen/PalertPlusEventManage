# coding: utf-8
# =============================
# 用來建立每個事件的檔案詳細資料表
# =============================
import os
import pandas as pd
import waveform
import logging

def allFileListCsv():
    try:
        dirList = os.listdir('eqdata')
        for dir in dirList:
            #if not os.path.isfile('eqdata/'+dir+'/'+dir+'.csv'):
                fileList = [file for file in os.listdir(
                    'eqdata/'+ dir + '/allFile/')]
                sizes = [os.path.getsize('eqdata/'+dir + '/allFile/'+file) for file in fileList]
                stata = [1 for file in fileList]
                #maxGal = [waveform.maxGal('eqdata/'+dir+'/'+file) for file in fileList]
                table = {
                    "name": fileList,
                    "size": sizes,
                    "status": stata,
                    #"maxGal": maxGal
                }
                df = pd.DataFrame(table)
                df.to_csv('eqdata/'+dir+'/'+dir+'.csv', encoding='utf-8')
    except Exception as e:
                logging.error(e)


def fileListCsv(dir):
    try:
        fileList = [file for file in os.listdir('eqdata/'+dir) if '.mseed' in file]
        sizes = [os.path.getsize('eqdata/'+dir+'/'+f) for f in fileList]
        stata = [1 for f in fileList]
        maxGal = [waveform.maxGal('eqdata/'+dir+'/'+f) for f in fileList]
        table = {
            "name": fileList,
            "size": sizes,
            "status": stata,
            "maxGal": maxGal
        }
        df = pd.DataFrame(table)
        df.to_csv('eqdata/'+dir+'/'+dir+'.csv', encoding='utf-8')
        # print(os.path.isfile('eqdata/'+dir+'/'+dir+'.csv'))
    except Exception as e:
                logging.error(e)
# fileListCsv()
