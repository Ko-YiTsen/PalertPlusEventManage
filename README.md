# PalertPlusEventManage

**eqdata**
>event(%Y%m%d%H%M%S)
>>allFile(.csv, .mseed, .sac)
>>event.csv(file list)
>>event.png(download from scwc)

**templates and app.py**  
web html files and flask run

**chromedriver**  
2 version： one for win,another for linux

**main.py(run scweb_scraper.py, cwb_scraper.py every 10 mins)**  
collect eq events list, save to scweb_cwb_scraper.csv, cwb_scraper.csv

**ftpEvent**  
download files from ftp serve

**mFileList.py**  
Creat a file list for each event

**waveform.py**  
plot daigram from .mseed file

**palert.yml**  
env set
