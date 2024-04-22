# Schedule Library imported
from doctest import OutputChecker
from gundem_scraper import EksiGundemSpider
from research_scraper import EksiTrendGundemSpider
#import schedule
import time
import datetime
import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
  
# Functions setup

def job():
    process = CrawlerProcess(settings={
            'BOT_NAME': 'eksispiders',
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
            'ROBOTSTXT_OBEY': True,
            'CONCURRENT_REQUESTS': 32,
            'DOWNLOAD_DELAY': 0.2,
            'DUPEFILTER_DEBUG': True
        })
    process.crawl(EksiTrendGundemSpider)
    process.start()

  
#schedule.every(15).minutes.do(job)
#schedule.every().hour.do(job)
#schedule.every().day.at("10:30").do(job)
#schedule.every().monday.do(job)
#schedule.every().wednesday.at("13:15").do(job)
#schedule.every().minute.at(":17").do(job)

#while True:
    #schedule.run_pending()
    #time.sleep(1)