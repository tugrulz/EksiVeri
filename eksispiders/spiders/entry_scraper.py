import inspect
import sys
import selector_constants as sel_cons
import eksi_scrape_lib as eksi_lib
import scrapy
from scrapy.crawler import CrawlerProcess
import csv
import os
import click
from scrapy.utils.project import get_project_settings


class EksiEntryFinalSpider(scrapy.Spider):
    name = "eksi_entry_final_spider"
    handle_httpstatus_list = [404, 503]

    def __init__(self, single_entry=None, file_name='entry_id_list.csv', col_no='0', content_limit='280',
                 tag_name='scraped_entries', *args, **kwargs):
        super(EksiEntryFinalSpider, self).__init__(*args, **kwargs)
        self.content_limit = int(content_limit)
        self.col_no = int(col_no)
        self.file_name = file_name
        self.tag_name = tag_name
        self.single_entry = single_entry
        self.start_urls = ['https://eksisozluk.com']

    def parse(self, response):
        
        if not os.path.exists('data'):
            os.mkdir('data')
        absolute_path = 'data/'
        def_file = absolute_path + self.tag_name + '.csv'
        long_file = absolute_path + self.tag_name + '_long.csv'
        link_file = absolute_path + self.tag_name + '_links.csv'

        with open(def_file, encoding='utf-8', mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["title","entry_id", "author", 'is_caylak', "date", "edit_date", "fav_num", "short_content"])
        with open( long_file, encoding = 'utf-8', mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["title","entry_id", "content"])
        with open( link_file, encoding = 'utf-8', mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["title","entry_id", "link", "link_text"])
        if self.single_entry:
            yield scrapy.Request(
                url='https://eksisozluk.com/entry/' + self.single_entry,
                callback=self.parse_entry
            )
        else:
            with open(self.file_name, 'r', encoding='utf-8') as read_obj:
                # pass the file object to reader() to get the reader object
                csv_reader = csv.reader(read_obj)
                # Iterate over each row in the csv using reader object
                for row in csv_reader:
                    # row variable is a list that represents a row in csv
                    entry_id = row[self.col_no]
                    yield scrapy.Request(
                        url='https://eksisozluk.com/entry/' + str(entry_id),
                        callback=self.parse_entry
                    )

    def parse_entry(self, response):
        absolute_path = 'data/'
        #print("                           absolute path: " + absolute_path)
        if response.status == 503:
            with open(absolute_path + 'remaining_topics.csv', encoding='utf-8', mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([response.request.url])
        if response.status == 404:
            with open(absolute_path + '404_entries.csv', encoding='utf-8', mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([response.request.url])
        if response.status == 200:
            topic_id = response.css(sel_cons.TOPIC_ID_SELECTOR).extract_first()
            if topic_id:
                def_file = absolute_path + self.tag_name + '.csv'
                long_file = absolute_path + self.tag_name + '_long.csv'
                link_file = absolute_path + self.tag_name + '_links.csv'

                eksi_lib.parse_single_entry(response, self.content_limit, def_file, long_file, link_file)

@click.command()
@click.option("--single_entry", type=click.IntRange(min=0), default=0, show_default=False)
@click.argument("tag_name")
@click.argument("file_name", type=click.Path(exists=True, file_okay=True), default="entry_id_list.csv")
@click.argument("col_no", type=click.INT, default=0)
@click.argument("content_limit", type=click.IntRange(min=1), default=280)
def run(single_entry, tag_name, file_name, col_no, content_limit):
    # print(inspect.stack())
    # return
    # script_name = inspect.stack()[0][1]
    # # file_name = os.path.abspath(file_name)
    #
    # single_entry_str = ""
    # if single_entry is not 0:
    #     single_entry_str = " -a single_entry=" + str(single_entry)
    #
    # cmd = "scrapy runspider " + script_name + single_entry_str + " -a file_name=" + file_name + " -a col_no=" + \
    #       str(col_no) + " -a content_limit=" + str(content_limit) + " -a tag_name=" + tag_name
    #
    # print(cmd)
    # os.system(cmd)
    if single_entry is not 0:
        process = CrawlerProcess(settings={
            'BOT_NAME': 'eksispiders',
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
            'ROBOTSTXT_OBEY': True,
            'CONCURRENT_REQUESTS': 32,
            'DOWNLOAD_DELAY': 0.2,
            'DUPEFILTER_DEBUG': True
        })
        process.crawl(EksiEntryFinalSpider, single_entry=str(single_entry), file_name=file_name, col_no=str(col_no),
                      content_limit=str(content_limit), tag_name=tag_name)
        process.start()
    else:
        process = CrawlerProcess(settings={
            'BOT_NAME': 'eksispiders',
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
            'ROBOTSTXT_OBEY': True,
            'CONCURRENT_REQUESTS': 32,
            'DOWNLOAD_DELAY': 0.2,
            'DUPEFILTER_DEBUG': True
        })
        process.crawl(EksiEntryFinalSpider,  file_name=file_name, col_no=str(col_no),
                      content_limit=str(content_limit), tag_name=tag_name)
        process.start()
