from apscheduler.schedulers.background import BackgroundScheduler
from uniJobCatch.unsw import UNSWJobScraper
# 导入其他大学的爬虫...

def schedule_jobs():
    scheduler = BackgroundScheduler()
    
    # 每天凌晨2点运行爬虫
    scheduler.add_job(
        UNSWJobScraper().scrape_jobs,
        'cron',
        hour=2
    )
    
    scheduler.start() 