# coding: utf-8
from flask import Flask, json, render_template, request, jsonify, send_from_directory, send_file, redirect, url_for
import csv
import folium
import pandas as pd
import os
import datetime
import zipfile
from io import BytesIO
import pygsheets

import logging
import sys

# 外部函式
import waveform
import mFileList
import ftpEvent

logging.basicConfig(level=logging.INFO,format='%(levelname)s-[%(asctime)s]-%(message)s',datefmt='%Y-%m-%d %H:%M:%S',
                    filename='webLog.log', filemode='a')

app = Flask(__name__, static_url_path='/img_eq', static_folder='eqdata/')


@app.route('/')
# @app.route('/home')
# def home_page():
#     return render_template('home.html')

# 事件列表
@app.route('/')
def index():
    try:
        #foliumMap底圖
        start_coords = (23.5, 121)
        map = folium.Map(
                        location=start_coords,
                        zoom_start=7,
                        min_zoom=7,
                        tiles=None
                        )

        folium.TileLayer(
        name='alidade_smooth',
        tiles='https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png?api_key=c449f947-e798-4b9c-91bc-86b3d0e1e20d',
        attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
        maxNativeZoom = 7,
        minZoom = 7
        ).add_to(map)
        folium.TileLayer(
        name='openstreetmap.org',
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxNativeZoom = 7,
        minZoom = 7
        ).add_to(map)
        folium.TileLayer(
        name='arcgisonline',
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        maxNativeZoom = 7,
        minZoom = 7
        ).add_to(map)
        
        #測站位置

        gc = pygsheets.authorize(service_account_file='StationList.json')

        url = 'https://docs.google.com/spreadsheets/d/188xTDpcKH33QId-iQF-aeqhT5BylrZe3pQvYxWVhmzw/edit#gid=2026807724'
        sht = gc.open_by_url(url)

        ws = sht.worksheet_by_title('Palert Plus 測站儀器列表')
        df = ws.get_as_df(start='A1', index_colum=0, empty_value='NaN', include_tailing_empty=False)
        df['經度(WGS84)'] = pd.to_numeric(df['經度(WGS84)'], errors='coerce')
        df = df.dropna(subset=['經度(WGS84)'])
        for index, row in df.iterrows():
            icon_url = 'triangle.png'
            icon = folium.features.CustomIcon(icon_url,icon_size=(15, 15))
            iframe = folium.IFrame(
            'Site No. : '+str(row['測站編號'])+
            '<br>'+"Machine No. : "+str(row['機器編號'])+
            '<br>'+'Latitude : '+str(row['經度(WGS84)'])+
            '<br>'+'Longitude : '+str(row['緯度(WGS84)'])
            )
            popup = folium.Popup(iframe, min_width=200, max_width=200)
            folium.Marker(
                location = [row['緯度(WGS84)'], row['經度(WGS84)']],
                popup = popup,
                icon=icon
                ).add_to(map)
        
        #取得當下月份的事件列表    
        nowTime = str(datetime.datetime.now())
        nowYear = nowTime.split('-')[0]
        nowMonth = nowTime.split('-')[1]
        date = nowYear+'-'+nowMonth
        evenlist = pd.read_csv('scweb_cwb_scraper.csv', dtype={'Number': object})
        evenlist["Origin Time"] = evenlist["Origin Time"].astype("category")
        mask = evenlist["Origin Time"].str.lower().str.startswith(date)
        currnet_data = evenlist[mask]
        
        global datas
        datas = []
        for index, row in currnet_data.iterrows():
                data = {
                        'ID':row['ID'],
                        'No':('Local' if str(row['Number']) == '000' else str(row['Number'])),
                        'OriginTime':row['Origin Time'],
                        'Mag':row['Magnitude'],
                        'Lat':row['Latitude'],
                        'Long':row['longtitude']
                    }
                datas.append(data)
                
                iframe = folium.IFrame(
                'ID:'+str(row['ID']) + 
                '<br>'+"Origin Time:"+'<br>'+str(row['Origin Time']) +
                '<br>'+'Magnitude:'+str(row['Magnitude'])+
                '<br>'+'Latitude:'+str(row['Latitude'])+
                '<br>'+'Longitude:'+str(row['longtitude'])+
                '<br>'+'<a href='+str(row['Link'])+' target="_blank">More Info</a>'
                )
                popup = folium.Popup(iframe, min_width=200, max_width=200)
                folium.CircleMarker(
                    radius = 1.2**(5.24+1.44*row['Magnitude']),
                    location = [row['Latitude'], row['longtitude']], 
                    popup = popup,
                    color="white",
                    weight = 1,
                    fill=True,
                    fill_color="green",
                ).add_to(map)
                
        folium.LayerControl().add_to(map)
        map.save('templates/map.html')
        
    except Exception as e:
        logging.error(str(e))
        
    return render_template('dataList.html',datas=datas, map=map, date=date)


@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        start_coords = (23.5, 121)
        map = folium.Map(
                        location=start_coords,
                        zoom_start=7,
                        tiles=None
                        )

        folium.TileLayer(
        name='alidade_smooth',
        tiles='https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png?api_key=c449f947-e798-4b9c-91bc-86b3d0e1e20d',
        attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
        maxNativeZoom = 7,
        minZoom = 7
        ).add_to(map)
        folium.TileLayer(
        name='openstreetmap.org',
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxNativeZoom = 7,
        minZoom = 7
        ).add_to(map)
        folium.TileLayer(
        name='arcgisonline',
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        maxNativeZoom = 7,
        minZoom = 7
        ).add_to(map)
        
        gc = pygsheets.authorize(service_account_file='StationList.json')

        url = 'https://docs.google.com/spreadsheets/d/188xTDpcKH33QId-iQF-aeqhT5BylrZe3pQvYxWVhmzw/edit#gid=2026807724'
        sht = gc.open_by_url(url)

        ws = sht.worksheet_by_title('Palert Plus 測站儀器列表')
        df = ws.get_as_df(start='A1', index_colum=0, empty_value='NaN', include_tailing_empty=False)
        df['經度(WGS84)'] = pd.to_numeric(df['經度(WGS84)'], errors='coerce')
        df = df.dropna(subset=['經度(WGS84)'])
        for index, row in df.iterrows():
            icon_url = 'triangle.png'
            icon = folium.features.CustomIcon(icon_url,icon_size=(15, 15))
            iframe = folium.IFrame(
            'Site No. : '+str(row['測站編號'])+
            '<br>'+"Machine No. : "+str(row['機器編號'])+
            '<br>'+'Latitude : '+str(row['經度(WGS84)'])+
            '<br>'+'Longitude : '+str(row['緯度(WGS84)'])
            )
            popup = folium.Popup(iframe, min_width=200, max_width=200)
            folium.Marker(
                location = [row['緯度(WGS84)'], row['經度(WGS84)']],
                popup = popup,
                icon=icon
                ).add_to(map)
        
        print("search")
        if request.method == 'POST':
            datepicker = request.form['datepicker']
            print("search end")
            #print(datepicker)
            
            df = pd.read_csv('scweb_cwb_scraper.csv', dtype={'Number': object})
            df["Origin Time"] = df["Origin Time"].astype("category")
            mask = df["Origin Time"].str.lower().str.startswith(datepicker)
            filter_df = df[mask]
            # print(filter_df)
            datas = []
            for index, row in filter_df.iterrows():
                data = {
                        'ID':row['ID'],
                        'No':('Local' if str(row['Number']) == '000' else str(row['Number'])),
                        'OriginTime':row['Origin Time'],
                        'Mag':row['Magnitude'],
                        'Lat':row['Latitude'],
                        'Long':row['longtitude']
                    }
                datas.append(data)
                
                iframe = folium.IFrame(
                'ID:'+str(row['ID']) + 
                '<br>'+"Origin Time:"+'<br>'+str(row['Origin Time']) +
                '<br>'+'Magnitude:'+str(row['Magnitude'])+
                '<br>'+'Latitude:'+str(row['Latitude'])+
                '<br>'+'Longitude:'+str(row['longtitude'])+
                '<br>'+'<a href='+str(row['Link'])+' target="_blank">More Info</a>'
                )
                popup = folium.Popup(iframe, min_width=200, max_width=200)
                folium.CircleMarker(
                    radius = 1.2**(5.24+1.44*row['Magnitude']),
                    location = [row['Latitude'], row['longtitude']], 
                    popup = popup,
                    color="white",
                    weight = 1,
                    fill=True,
                    fill_color="green",
                ).add_to(map)
        
        folium.LayerControl().add_to(map)
        map.save('templates/map.html')
        
    except Exception as e:
        logging.error(str(e)) 
        
    return jsonify({'htmlresponse': render_template('response.html', datas=datas, map=map,datepicker=datepicker)})


# 個別事件畫面
@app.route('/event/<eqID>', methods=['GET', 'POST'])
def manageEvent(eqID):
    statusDict = {}
    #maxgalDict = {}
    with open('eqdata/'+eqID+'/'+eqID+'.csv', 'rt') as fileX:
        filereader = csv.reader(fileX)

        for row in filereader:
            key = row[1]
            statusDict[key] = row[3]
            #maxgalDict[key] = row[4]

    with open('scweb_cwb_scraper.csv', 'rt', encoding="utf8") as file:
        filereader = csv.reader(file)
        event = {}
        for row in filereader:
            if row[1] == eqID:

                event = {
                    'ID': row[1],
                    'No': ('Local' if str(row[2]) == '000' else row[2]),
                    'Intensity': row[3],
                    'Time': row[4],
                    'Loc': row[5],
                    'Mag': row[9],
                    'Long': row[7],
                    'Lat': row[6],
                    'Dept': row[8],
                    'OriginID': (str(row[1])+str(row[9]).replace('.', '') if row[2] == '000' else str(row[1])+str(row[9]).replace('.', '')+row[2])

                }
            # 0,ID,Number,LargestIntensity,Origin Time,Location,Latitude,longtitude,Depth,Magnitude,Link
    #eventPath = 'eqdata/'+eqID  # eqdata\20210708073102
    filespath = 'eqdata/'+eqID + '/allFile'
    fileList = os.listdir(filespath)
    eventCount = os.listdir('eqdata').index(eqID)
    eventList = os.listdir('eqdata')[eventCount-3:eventCount+3]
    infos = []
    for file in fileList:
        if 'csv' in file:
            filePath = 'eqdata/'+eqID + '/allFile/'+file
            fileInfo = {
                'size': os.path.getsize(filePath),
                'name': file,
                'station': file.split('_')[2],
                #'imgPath': eqID+'/'+file.replace('mseed', 'png'),
                'status': statusDict[file],
                #'maxGal': maxgalDict[file]
            }

            infos.append(fileInfo)

    # fileInfo={}

    return render_template('manageEvent.html', event=event, infos=infos, eventList=eventList)


@app.route('/<eqID>/delete_file/<name>', methods=['POST'])
def delete_file(eqID, name):
    print('delete'+eqID+'  '+name)
    df = pd.read_csv('eqdata/'+eqID+'/'+eqID+'.csv')
    df.loc[df["name"] == name, "status"] = '0'
    df.to_csv('eqdata/'+eqID+'/'+eqID+'.csv', index=False)
    return redirect(url_for('manageEvent', eqID=eqID))


@app.route('/<eqID>/add_file/<name>', methods=['POST'])
def add_file(eqID, name):
    print('add'+eqID+'  '+name)
    df = pd.read_csv('eqdata/'+eqID+'/'+eqID+'.csv')
    df.loc[df["name"] == name, "status"] = '1'
    df.to_csv('eqdata/'+eqID+'/'+eqID+'.csv', index=False)
    return redirect(url_for('manageEvent', eqID=eqID))


# 按按鈕後重抓事件檔案(可指定時間範圍)
@app.route('/event/<eqID>/reftp/<tz>')
def reftp(eqID, tz):
    log=[]
    dirpath = os.path.join(app.root_path, 'eqdata', eqID)
    flist = os.listdir(dirpath)
    # 刪掉舊檔案
    for f in flist:
        if '.mseed' in f or '.png' in f:
            os.remove(os.path.join(dirpath, f))

    start = int(tz.split('_')[0])
    end = int(tz.split('_')[1])
    try:
        ftp = ftpEvent.ftpLogin()
        log = ftpEvent.ftpEvent(ftp,eqID,start,end)
    except Exception as e:
        logging.error(e)
        
    mFileList.fileListCsv(eqID)

    return render_template('reftp.html',logs=log)


@app.route('/event/<eqID>/download', methods=['GET', 'POST'])
def download_file(eqID):

    print('click download')
    # fnames = request.form.get("fnames")
    # fname_list = json.loads(fnames)
    fname_str = request.args.get("fnames")
    fname_list = eval(fname_str)

    # fname_list = request.form.getlist('f_name[]')

    # # while (0 in fname_list):
    # #     fname_list.remove(0)
    print('selected files: ')
    print(fname_list)

    # # print(app.root_path)
    dirpath = os.path.join(app.root_path, 'eqdata', eqID)
    print('download from: '+dirpath)

    # print('exist file in dir: ')
    # print(os.listdir(dirpath))

    if len(fname_list) == 1:

        print('download this: '+os.path.join(dirpath, 'allFile',fname_list[0]))
        dlpath = os.path.join(dirpath,'allFile',fname_list[0]).replace('\\', '/')
        print('download this: '+dlpath)
        print(os.path.isfile(dlpath))
        return send_file(dlpath, as_attachment=True)
        
    elif len(fname_list) > 1:
        dl_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'.zip'
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for _file in fname_list:
                with open(os.path.join(dirpath,'allFile', _file), 'rb') as fp:
                    zf.writestr(_file, fp.read())
                print(_file+' add to zip')
        memory_file.seek(0)
        return send_file(memory_file, attachment_filename=dl_name, as_attachment=True)


if __name__ == '__main__':
     app.run(host="0.0.0.0",debug=True)

