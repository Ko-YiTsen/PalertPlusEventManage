# coding: utf-8
def check_cwb_routine():
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    import time
    import scweb_cwb_scraper
    import cwb_scraper
    import logging
    
    logging.basicConfig(level=logging.INFO,format='%(levelname)s-[%(asctime)s]-%(message)s',datefmt='%Y-%m-%d %H:%M:%S',filename='scrapLog.log', filemode='a')
    
    def job():
        print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            #cwb_main() #跑程式的地方
        if not scweb_cwb_scraper.scweb_cwb():
                cwb_scraper.cwb_scraper()
            
    if __name__=='__main__':
            job_defaults = { 'max_instances': 2 }
            sched = BackgroundScheduler(timezone='MST', job_defaults=job_defaults)
            intervalTrigger=IntervalTrigger(seconds=600)
            sched.add_job(job, intervalTrigger, id='600_second_job')
            sched.start()
            print('=== end. ===')
            while True:
                time.sleep(1)
check_cwb_routine()
