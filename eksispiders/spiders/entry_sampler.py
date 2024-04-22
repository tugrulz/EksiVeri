import sys
import selector_constants as sel_cons
import eksi_scrape_lib as eksi_lib
import click
import scrapy
import csv
import random 
import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class EksiEntryFinalSpider(scrapy.Spider):
    name = "eksi_entry_final_spider"
    current_entry = 0
    current_entry_index = 0
    handle_httpstatus_list = [404, 503]
    count_404 = 0
    start_entry = None
    end_entry = None
    sample_size = None
    def __init__(self, start_entry = None, end_entry = None, sample_size=None, content_limit='280', tag_name='scraped_entries', *args, **kwargs):
            super(EksiEntryFinalSpider, self).__init__(*args, **kwargs)
            self.content_limit = int(content_limit)
            self.tag_name= tag_name
            self.start_entry = start_entry
            self.end_entry = end_entry
            self.sample_size = sample_size
            self.start_urls = ['https://eksisozluk.com']
    def parse(self, response):
        if self.start_entry and self.sample_size and self.end_entry:
            if (int(self.end_entry) - int(self.start_entry)) > int(self.sample_size) and int(self.sample_size) > 0 and int(self.start_entry) > 0 and int(self.end_entry) > 0:
                random_entry_id_list = random.sample(list(range(int(self.start_entry), int(self.end_entry))), int(self.sample_size))
                
                if not os.path.exists('input'):
                    os.mkdir('input')
                if not os.path.exists('data'):
                    os.mkdir('data')

                with open('input/random_ids.csv', encoding = 'utf-8', mode='a', newline='') as f:
                        writer = csv.writer(f)
                        for s in random_entry_id_list:
                            writer.writerow([s])

                def_file = 'data/' + self.tag_name + '.csv'
                long_file = 'data/' + self.tag_name + '_long.csv'
                link_file = 'data/' + self.tag_name + '_links.csv'

                with open( def_file, encoding = 'utf-8', mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["title","entry_id", "author", 'is_caylak', "date", "edit_date", "fav_num", "short_content"])
                with open( long_file, encoding = 'utf-8', mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["title","entry_id", "content"])
                with open( link_file, encoding = 'utf-8', mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["title","entry_id", "link", "link_text"])
            
                for entry_id in random_entry_id_list:
                    yield scrapy.Request(
                        url='https://eksisozluk.com/entry/' + str(entry_id),
                        callback=self.parse_entry,
                        headers={'user-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
                    )
            else:
                print("You should enter a valid start entry id, end entry id and sample size to scrape.")
        else:
            print("You should enter a start entry id, end entry id and sample size to scrape.")
    def parse_entry(self, response):
        if response.status == 503:
            with open('data/remaining_topics.csv', encoding = 'utf-8', mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([response.request.url])
        if response.status == 404:
            with open('data/404_topics.csv', encoding = 'utf-8', mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([response.request.url.split("entry/")[1]])
        if response.status == 200:
            topic_id = response.css(sel_cons.TOPIC_ID_SELECTOR).extract_first()
            if topic_id:
                def_file = 'data/' + self.tag_name + '.csv'
                long_file = 'data/' + self.tag_name + '_long.csv'
                link_file = 'data/' + self.tag_name + '_links.csv'

                eksi_lib.parse_single_entry(response, self.content_limit, def_file, long_file, link_file)
                    

@click.command()
@click.argument("start_entry", type=click.IntRange(min=1))
@click.argument("end_entry", type=click.IntRange(min=2))
@click.argument("sample_size", type=click.IntRange(min=1))
@click.argument("content_limit", type=click.IntRange(min=1), default=280)
def run(start_entry, end_entry, sample_size, content_limit):
    # script_name = sys.argv[0]
    # os.system("scrapy runspider " + script_name + content_limit + start_entry + end_entry + str(sample_size))
    process = CrawlerProcess(settings={
        'BOT_NAME': 'eksispiders',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 32,
        'DOWNLOAD_DELAY': 0.2,
        'DUPEFILTER_DEBUG': True
    })
    process.crawl(EksiEntryFinalSpider, start_entry=start_entry, end_entry=end_entry, sample_size=sample_size, content_limit=content_limit)
    process.start()
