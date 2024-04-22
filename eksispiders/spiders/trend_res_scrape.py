import sys
import click
import selector_constants as sel_cons
import eksi_scrape_lib as eksi_lib
import os
import scrapy
import csv
from urllib.parse import unquote_plus
from urllib.parse import quote_plus

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from datetime import datetime


class EksiTrendGundemSpider(scrapy.Spider):
    name = "eksi_trend_gundem_spider"
    handle_httpstatus_list = [404, 503]
    content_limit = 280
    col_no = 2 
    file_name = 'gundem_list.csv'
    page_no=None
    sukela = 0
    now = datetime.now()
    scrape_time = now.strftime("%H:%M:%S")
    out_tag = "out_" + now.strftime("%H_%M_%S")
    scrape_date = datetime.today().strftime('%d_%m_%Y')
    searched_links = []
    def __init__(self, file_name='gundem_list.csv',  *args, **kwargs):
            super(EksiTrendGundemSpider, self).__init__(*args, **kwargs)
            self.file_name = 'gundem_' + self.scrape_date + '.csv'
            self.start_urls = ['https://eksisozluk.com/basliklar/gundem']
            self.page_no = 0
            if not os.path.exists('data'):
                os.mkdir('data')
            absolute_path = 'data/'
            if not os.path.exists(absolute_path + self.file_name):
                with open(absolute_path + self.file_name, encoding = 'utf-8', mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['topic', 'entry_count', 'link'])
            def_file = absolute_path + self.out_tag + '.csv'
            long_file = absolute_path + self.out_tag + '_long.csv'
            link_file = absolute_path + self.out_tag + '_links.csv'
            with open( def_file, encoding = 'utf-8', mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["title","entry_id", "author", "date", "edit_date", "fav_num", "short_content", "ranking"])
            with open( long_file, encoding = 'utf-8', mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["title","entry_id", "content"])
            with open( link_file, encoding = 'utf-8', mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["title","entry_id", "link", "link_text"])
    def parse(self, response):
       
        absolute_path = 'data/'
        eksi_lib.create_int_output_files
        with open(absolute_path + self.file_name, 'r', encoding='utf-8') as read_obj:
                # pass the file object to reader() to get the reader object
                csv_reader = csv.reader(read_obj)
                # Iterate over each row in the csv using reader object
                for row in csv_reader:
                    # row variable is a list that represents a row in csv
                    topic_link = row[self.col_no]
                    self.searched_links.append(topic_link)
                    if 'https://eksisozluk.com' in topic_link:

                        
                            yield scrapy.Request(
                                url=topic_link,
                                callback=self.parse_topic
                            )
                    else:
                        topic_link = 'https://eksisozluk.com/?q=' + quote_plus(topic_link)
                        yield scrapy.Request(
                            url=topic_link,
                            callback=self.parse_mid
                        )
        yield scrapy.Request(
            url='https://eksisozluk.com/basliklar/gundem',
            callback=self.parse_gundem
        )
    def parse_mid(self, response):
        absolute_path = 'data/'
        if response.status == 503:
            with open( absolute_path + 'remaining_topics.csv', encoding = 'utf-8', mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([response.request.url])
        if response.status == 404:
            error_topic = response.request.url
            if '?q=' in error_topic:
                with open(absolute_path + '404_topic.csv', encoding = 'utf-8', mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([unquote_plus(error_topic.split('?q=')[1])])
            else:
                with open(absolute_path + '404_topic_link.csv', encoding = 'utf-8', mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([error_topic])
        if response.status == 200:
            if self.page_no:
                if self.page_no > 1:
                    yield scrapy.Request(
                        response.urljoin(response.request.url.split('?')[0] + '?p=' + str(self.page_no)),
                        callback=self.parse_topic
                    )
                elif self.page_no is 1:
                    yield scrapy.Request(
                        response.urljoin(response.request.url.split('?')[0]),
                        callback=self.parse_topic,
                        dont_filter = True
                    )
                else:
                    print("Invalid page no")
            else:
                if self.sukela is 0:
                    yield scrapy.Request(
                        response.urljoin(response.request.url.split('?')[0]),
                        callback=self.parse_topic,
                        dont_filter = True
                    )
                elif self.sukela is 1:
                    yield scrapy.Request(
                        response.urljoin(response.request.url.split('?')[0] + '?a=nice'),
                        callback=self.parse_topic
                    )
                elif self.sukela is 2:
                    yield scrapy.Request(
                        response.urljoin(response.request.url.split('?')[0] + '?a=dailynice'),
                        callback=self.parse_topic
                    )  
    def parse_gundem(self, response):    
        if response.status == 200:
            absolute_path = 'data/'
            for topic_block in response.css(sel_cons.SET_SELECTOR):
                topic_name = topic_block.css("a::text").extract_first().strip()
                entry_count = topic_block.css("a > small::text").extract_first()
                if entry_count:
                    entry_count.strip()
                    if 'b' in entry_count:
                        entry_count = entry_count.replace(',', '.')
                        entry_count = entry_count.replace('b', '')
                        entry_count = float(entry_count) * 1000
                topic_link = 'https://eksisozluk.com' + topic_block.css('a::attr(href)').extract_first().split('?')[0]
                if topic_link not in self.searched_links:
                    with open( absolute_path + self.file_name, encoding = 'utf-8', mode='a', newline='') as f:
                                    writer = csv.writer(f)
                                    writer.writerow([topic_name, entry_count, topic_link])
                    yield scrapy.Request(
                        response.urljoin(topic_link),
                        callback=self.parse_topic
                    )
            if self.page_no < 1:

                self.page_no = self.page_no + 1
                yield scrapy.Request(
                    response.urljoin(response.request.url + '?p=2'),
                    callback=self.parse_gundem
                )
            elif self.page_no < 2:
                self.page_no = self.page_no + 1
                last_page = response.css(sel_cons.LAST_PAGE_SELECTOR).extract_first()
                print(last_page)
                if last_page:
                    for x in range(3, int(last_page) + 1):
                        yield scrapy.Request(
                            response.urljoin(response.request.url.split('?')[0] + '?p=' + str(x)),
                            callback=self.parse_gundem
                        )
            
    def parse_topic(self, response):
        absolute_path = 'data/'
        if response.status == 503:
            with open( absolute_path + 'remaining_topics.csv', encoding = 'utf-8', mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([response.request.url])
        if response.status == 404:
            with open( absolute_path + '404_topics.csv', encoding = 'utf-8', mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([response.request.url])
        if response.status == 200:
            topic_id = response.css(sel_cons.TOPIC_ID_SELECTOR).extract_first()
            if topic_id:
                def_file = absolute_path + self.out_tag + '.csv'
                long_file = absolute_path + self.out_tag + '_long.csv'
                link_file = absolute_path + self.out_tag + '_links.csv'
                
                eksi_lib.parse_topic_entry(response, self.content_limit, def_file, long_file, link_file)    
                
                current_page = response.css(sel_cons.CURRENT_PAGE_SELECTOR).extract_first()
                last_page = response.css(sel_cons.LAST_PAGE_SELECTOR).extract_first()

                #send request to rest of the pages
                if current_page and last_page:
                    if current_page is '1':
                        if int(last_page) > 3:
                            last_page = '3' 
                        for x in range(2, int(last_page) + 1):
                            if self.sukela is 0 and not self.page_no:
                                    yield scrapy.Request(
                                        response.urljoin(response.request.url.split('?')[0] + '?p=' + str(x)),
                                        callback=self.parse_topic
                                    )
                            elif self.sukela is 1:
                                yield scrapy.Request(
                                    response.urljoin(response.request.url.split('?')[0] + '?a=nice&p=' + str(x)),
                                    callback=self.parse_topic
                                )
                            elif self.sukela is 2:
                                if int(current_page) < int(last_page):
                                    yield scrapy.Request(
                                        response.urljoin(response.request.url.split('?')[0] + '?a=dailynice&p=' + str(x)),
                                        callback=self.parse_topic
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
    process.crawl(EksiTrendGundemSpider, file_name=file_name )
    process.start()
