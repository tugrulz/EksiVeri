import sys
import selector_constants as sel_cons
import eksi_scrape_lib as eksi_lib
import click
import scrapy
import csv
import os
from urllib.parse import quote_plus
from urllib.parse import unquote_plus

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class EksiBaslikFinalSpider(scrapy.Spider):
    name = "eksi_baslik_final_spider"
    handle_httpstatus_list = [404, 503]
    content_limit = 280
    col_no = 0
    file_name = 'topic_links_list.csv'
    page_no=None
    sukela = 0
    def __init__(self, single_topic=None, file_name='topic_links_list.csv', col_no='0', content_limit='280', page_no=None, sukela='1', *args, **kwargs):
            super(EksiBaslikFinalSpider, self).__init__(*args, **kwargs)
            self.content_limit = int(content_limit)
            self.col_no = int(col_no)
            self.file_name = file_name
            self.single_topic = single_topic
            if page_no:
                self.page_no = int(page_no)
            self.sukela = int(sukela)
            self.start_urls = ['https://eksisozluk.com']
    def parse(self, response):
        eksi_lib.create_int_output_files()    
        if self.single_topic:
            if 'https://eksisozluk.com' in self.single_topic:
                topic_link = self.single_topic
                #decide which type of scrape it would be
                if self.page_no:
                    if self.page_no > 1:
                        yield scrapy.Request(
                            url=topic_link + '?p=' + str(self.page_no),
                            callback=self.parse_topic
                        )
                    elif self.page_no is 1:
                        yield scrapy.Request(
                            url=topic_link,
                            callback=self.parse_topic
                        )
                    else:
                        print("Invalid page no")
                else:
                    if self.sukela is 0:
                        yield scrapy.Request(
                                url=topic_link,
                                callback=self.parse_topic
                            )
                    elif self.sukela is 1:
                        yield scrapy.Request(
                            url=topic_link + '?a=nice',
                            callback=self.parse_topic
                        )
                    elif self.sukela is 2:
                        yield scrapy.Request(
                            url=topic_link + '?a=dailynice',
                            callback=self.parse_topic
                        )
                    else:
                        print("Invalid sukela. Use sukela=0 for no ranking, sukela=1 for all time ranking, sukela=2 for daily ranking")
            else:
                        topic_link = 'https://eksisozluk.com/?q=' + quote_plus(self.single_topic)
                        yield scrapy.Request(
                            url=topic_link,
                            callback=self.parse_mid
                        )
        else:
            with open(self.file_name, 'r', encoding='utf-8') as read_obj:
                # pass the file object to reader() to get the reader object
                csv_reader = csv.reader(read_obj)
                # Iterate over each row in the csv using reader object
                for row in csv_reader:
                    # row variable is a list that represents a row in csv
                    topic_link = row[self.col_no]

                    if 'https://eksisozluk.com' in topic_link:

                        #decide which type of scrape it would be
                        if self.page_no:
                            print(self.page_no)
                            if self.page_no > 1:
                                yield scrapy.Request(
                                    url=topic_link + '?p=' + str(self.page_no),
                                    callback=self.parse_topic
                                )
                            elif self.page_no is 1:
                                yield scrapy.Request(
                                    url=topic_link,
                                    callback=self.parse_topic
                                )
                            else:
                                print("Invalid page no")
                        else:
                            if self.sukela is 0:
                                yield scrapy.Request(
                                        url=topic_link,
                                        callback=self.parse_topic
                                    )
                            elif self.sukela is 1:
                                yield scrapy.Request(
                                    url=topic_link + '?a=nice',
                                    callback=self.parse_topic
                                )
                            elif self.sukela is 2:
                                yield scrapy.Request(
                                    url=topic_link + '?a=dailynice',
                                    callback=self.parse_topic
                                )
                            else:
                                print("Invalid sukela. Use sukela=0 for no ranking, sukela=1 for all time ranking, sukela=2 for daily ranking")
                    else:
                        topic_link = 'https://eksisozluk.com/?q=' + quote_plus(topic_link)
                        yield scrapy.Request(
                            url=topic_link,
                            callback=self.parse_mid
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
                def_file = absolute_path + topic_id + '.csv'
                long_file = absolute_path + topic_id + '_long.csv'
                link_file = absolute_path + topic_id + '_links.csv'
                #set csv for different cases
                if self.sukela is 0 and self.page_no:
                    def_file = absolute_path + topic_id + '_page_' + str(self.page_no) + '.csv'
                    long_file = absolute_path + topic_id + '_page_' + str(self.page_no) + '_long.csv'
                    link_file = absolute_path + topic_id + '_page_' + str(self.page_no) + '_links.csv'
                elif self.sukela is 1:
                    def_file = absolute_path + topic_id + '_sukela_all.csv'
                    long_file = absolute_path + topic_id + '_sukela_all_long.csv'
                    link_file =  absolute_path + topic_id + '_sukela_all_links.csv'
                elif self.sukela is 2:
                    def_file = absolute_path + topic_id + '_sukela_daily.csv'
                    long_file = absolute_path + topic_id + '_sukela_daily_long.csv'
                    link_file = absolute_path + topic_id + '_sukela_daily_links.csv'
                if 'p=' not in response.request.url or self.page_no:
                    with open( def_file, encoding = 'utf-8', mode='w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(["title","entry_id", "author", "date", "edit_date", "fav_num", "short_content", "ranking"])
                    with open( long_file, encoding = 'utf-8', mode='w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(["title","entry_id", "content"])
                    with open( link_file, encoding = 'utf-8', mode='w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(["title","entry_id", "link", "link_text"])
                
                eksi_lib.parse_topic_entry(response, self.content_limit, def_file, long_file, link_file)    
                
                current_page = response.css(sel_cons.CURRENT_PAGE_SELECTOR).extract_first()
                last_page = response.css(sel_cons.LAST_PAGE_SELECTOR).extract_first()
                #send request to rest of the pages
                if current_page and last_page:
                    if current_page is '1':
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

@click.command()
@click.argument("sukela", type=click.Choice(choices=['0', '1', '2']))
@click.option("--page_no", type=click.IntRange(min=0), default=0, show_default=True,
              help="If a specific page is wanted to be scrape, it can be given here.")
@click.argument("file_name", type=click.Path(exists=True), default="topic_links_list.csv")
@click.argument("col_no", type=click.IntRange(min=0), default=0)
@click.argument("content_limit", type=click.IntRange(min=1), default=280)
def run(sukela, page_no, file_name, col_no, content_limit):
    # script_name = sys.argv[0]
    # page_no_str = ""
    # if page_no is not -1:
    #     page_no_str = str(page_no)
    #
    # os.system(
    #     "scrapy runspider " + script_name + file_name + str(col_no) + str(content_limit) + page_no_str + sukela)
    if page_no is 0:
        page_no = None

    process = CrawlerProcess(settings={
        'BOT_NAME': 'eksispiders',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 32,
        'DOWNLOAD_DELAY': 0.2,
        'DUPEFILTER_DEBUG': True
    })
    process.crawl(EksiBaslikFinalSpider, page_no=page_no, file_name=file_name, col_no=col_no,
                  content_limit=content_limit, sukela=sukela)
    process.start()
