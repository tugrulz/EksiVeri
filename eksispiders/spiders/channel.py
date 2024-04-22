import sys
import selector_constants as sel_cons
import click
import scrapy
import csv
import os
from urllib.parse import quote_plus

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class EksiBaslikChannelSpider(scrapy.Spider):
    name = "eksi_baslik_channel_spider"
    handle_httpstatus_list = [404, 503]
    col_no = 0 
    file_name = 'topic_links_list.csv'
    def __init__(self, single_topic=None, file_name='topic_links_list.csv', col_no='0', *args, **kwargs):
            super(EksiBaslikChannelSpider, self).__init__(*args, **kwargs)
            self.col_no = int(col_no)
            self.file_name = file_name
            self.single_topic = single_topic
            self.start_urls = ['https://eksisozluk.com']
    def parse(self, response):
        if not os.path.exists('data'):
            os.mkdir('data')
        absolute_path = 'data/'
        if not os.path.exists(absolute_path + 'topic_channels.csv'):
            with open( absolute_path + 'topic_channels.csv', encoding = 'utf-8', mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'name', 'channel'])
        if self.single_topic:
            if 'https://eksisozluk.com' in self.single_topic: 
                yield scrapy.Request(
                    url=self.single_topic,
                    callback=self.parse_topic
                )
            else:
                topic_link = 'https://eksisozluk.com/?q=' + quote_plus(self.single_topic)
                yield scrapy.Request(
                    url=topic_link,
                    callback=self.parse_topic
                ) 
        else:
            if os.path.exists(self.file_name):
                with open(self.file_name, 'r', encoding = 'utf-8') as read_obj:
                    # pass the file object to reader() to get the reader object
                    csv_reader = csv.reader(read_obj)
                    # Iterate over each row in the csv using reader object
                    for row in csv_reader:
                        # row variable is a list that represents a row in csv
                        topic_link = row[self.col_no]
                        if 'https://eksisozluk.com' in topic_link:
                            yield scrapy.Request(
                                url=topic_link,
                                callback=self.parse_topic
                            )
                        else:
                            topic_link = 'https://eksisozluk.com/?q=' + quote_plus(topic_link)
                            yield scrapy.Request(
                                url=topic_link,
                                callback=self.parse_topic
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
            topic_name = response.css(sel_cons.TOPIC_NAME_SELECTOR).extract_first()
            topic_id = response.css(sel_cons.TOPIC_ID_SELECTOR).extract_first()
            if topic_id: 
                # CHANNEL_SELECTOR = 'section > ul > li' 
                x = response.css('aside > section ::text').extract()[0]
                x = x.replace("\r"," ")
                x = x.replace("\n"," ")
                x = x.strip()
                channels = x.split(',')       
                with open(absolute_path + 'topic_channels.csv', encoding = 'utf-8', mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([topic_id, topic_name, channels])

@click.command()
@click.argument("file_name", type=click.Path(exists=True), default="topic_links_list.csv")
@click.argument("col_no", type=click.IntRange(min=0), default=0)
def run(file_name, col_no):
    # script_name = sys.argv[0]
    # os.system("scrapy runspider " + script_name + file_name + str(col_no))
    process = CrawlerProcess(settings={
        'BOT_NAME': 'eksispiders',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 32,
        'DOWNLOAD_DELAY': 0.2,
        'DUPEFILTER_DEBUG': True
    })
    process.crawl(EksiBaslikChannelSpider, file_name=file_name, col_no=col_no)
    process.start()
