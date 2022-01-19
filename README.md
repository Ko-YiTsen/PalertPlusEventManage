# PalertPlusEventManage

eqdata :
-event(%Y%m%d%H%M%S)
    - allFile(.csv, .mseed, .sac)
    -event.csv(file list)
    -event.png(download from scwc)

templates and app.py :
web html files and flask run

chromdriver :
2 version, one for win,another for linux

main.py(run scweb_scraper.py, cwb_scraper.py every 10 mins) :
collect eq events list-scweb_cwb_scraper.csv, cwb_scraper.csv

ftpEvent :
down files from ftp

waveform.py :
plot daigra from .mseed

palert1.yml :
env