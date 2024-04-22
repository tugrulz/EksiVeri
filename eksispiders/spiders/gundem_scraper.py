import sys
import click
import selector_constants as sel_cons
import os
import scrapy
import csv
from urllib.parse import unquote_plus
from urllib.parse import quote_plus

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class EksiGundemSpider(scrapy.Spider):
    name = "eksi_gundem_spider"
    handle_httpstatus_list = [404, 503]
    col_no = 0 
    file_name = 'keyword_list.csv'
    def __init__(self, file_name='gundem_list.csv',  *args, **kwargs):
            super(EksiGundemSpider, self).__init__(*args, **kwargs)
            self.file_name = file_name
            self.start_urls = ['https://eksisozluk.com/basliklar/gundem']
            self.page_no = 0
            if not os.path.exists('data'):
                os.mkdir('data')
            absolute_path = 'data/'
            with open(absolute_path + self.file_name, encoding = 'utf-8', mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['topic', 'entry_count', 'link'])
    def parse(self, response):    
        if response.status == 200:
            absolute_path = 'data/'
            #topic_keyword = unquote_plus(response.request.url.split('=')[1].split('&')[0])
            #print(topic_keyword)
            for topic_block in response.css(sel_cons.SET_SELECTOR):
                topic_name = topic_block.css("a::text").extract_first().strip()
                entry_count = topic_block.css("a > small::text").extract_first()
                if entry_count:
                    entry_count.strip()
                    if 'b' in entry_count:
                        entry_count = entry_count.replace(',', '.')
                        entry_count = entry_count.replace('b', '')
                        entry_count = float(entry_count) * 1000
                topic_link = 'https://eksisozluk.com' + topic_block.css('a::attr(href)').extract_first()
                with open( absolute_path + self.file_name, encoding = 'utf-8', mode='a', newline='') as f:
                                writer = csv.writer(f)
                                writer.writerow([topic_name, entry_count, topic_link])
            if self.page_no < 1:
                self.page_no = self.page_no + 1
                yield scrapy.Request(
                    response.urljoin(response.request.url + '?p=2'),
                    callback=self.parse
                )
            elif self.page_no < 2:
                self.page_no = self.page_no + 1
                last_page = response.css(sel_cons.LAST_PAGE_SELECTOR).extract_first()
                print(last_page)
                if last_page:
                    for x in range(3, int(last_page) + 1):
                        yield scrapy.Request(
                            response.urljoin(response.request.url.split('?')[0] + '?p=' + str(x)),
                            callback=self.parse
                        )
        
        #print((response.css('#container>#main>#content>#content-body>ul>li').extract_first()))

@click.command()
@click.argument("file_name", type=click.Path(exists=True), default="output.csv")
def run(file_name):
    # script_name = sys.argv[0]
    #
    # os.system(
    #     "scrapy runspider " + script_name + file_name + str(col_no) + str(content_limit) + single_keyword)
    process = CrawlerProcess(settings={
        'BOT_NAME': 'eksispiders',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 32,
        'DOWNLOAD_DELAY': 0.2,
        'DUPEFILTER_DEBUG': True
    })
    process.crawl(EksiGundemSpider, file_name=file_name )
    process.start()
