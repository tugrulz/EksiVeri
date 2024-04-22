import sys
import click
import os
import selector_constants as sel_cons
import scrapy
import csv
from urllib.parse import unquote_plus
from urllib.parse import quote_plus

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class EksiSimilarBaslikSpider(scrapy.Spider):
    name = "eksi_similar_baslik_spider"
    handle_httpstatus_list = [404, 503]
    col_no = 0 
    file_name = 'keyword_list.csv'
    def __init__(self, single_keyword= None, file_name='keyword_list.csv', col_no='0', *args, **kwargs):
            super(EksiSimilarBaslikSpider, self).__init__(*args, **kwargs)
            self.col_no = int(col_no)
            self.file_name = file_name
            self.single_keyword = single_keyword
            self.start_urls = ['https://eksisozluk.com']
    def parse(self, response):
        if not os.path.exists('data'):
            os.mkdir('data')
        absolute_path = 'data/'
        with open(absolute_path + 'related_topics.csv', encoding = 'utf-8', mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['keyword', 'name', 'entry_count', 'link'])
        if self.single_keyword:
            yield scrapy.Request(
                url='https://eksisozluk.com/basliklar/ara?SearchForm.Keywords='+ quote_plus(self.single_keyword) + '&SearchForm.NiceOnly=false&SearchForm.SortOrder=Date&p=1',
                callback=self.parse_similar
            ) 
        else:
            with open(self.file_name, 'r', encoding = 'utf-8') as read_obj:
                # pass the file object to reader() to get the reader object
                csv_reader = csv.reader(read_obj)
                # Iterate over each row in the csv using reader object
                for row in csv_reader:
                    # row variable is a list that represents a row in csv
                    keyword = row[self.col_no]
                    yield scrapy.Request(
                        url='https://eksisozluk.com/basliklar/ara?SearchForm.Keywords='+ quote_plus(keyword) + '&SearchForm.NiceOnly=false&SearchForm.SortOrder=Date&p=1',
                        callback=self.parse_similar
                    ) 
    def parse_similar(self, response):
        absolute_path = 'data/'    
        if response.status == 200:
            topic_keyword = unquote_plus(response.request.url.split('=')[1].split('&')[0])
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
                with open( absolute_path + 'related_topics.csv', encoding = 'utf-8', mode='a', newline='') as f:
                                writer = csv.writer(f)
                                writer.writerow([topic_keyword, topic_name, entry_count, topic_link])
            if response.request.url.endswith('&p=1'):
                yield scrapy.Request(
                    response.urljoin(response.request.url.split('&p=1')[0] + '&p=2'),
                    callback=self.parse_similar
                )
            elif response.request.url.endswith('&p=2'):
                last_page = response.css(sel_cons.LAST_PAGE_SELECTOR).extract_first()
                if last_page:
                    for x in range(3, int(last_page) + 1):
                        yield scrapy.Request(
                            response.urljoin(response.request.url.split('&p=2')[0] + '&p=' + str(x)),
                            callback=self.parse_similar
                        )
        
        #print((response.css('#container>#main>#content>#content-body>ul>li').extract_first()))

@click.command()
@click.argument("single_keyword")
@click.argument("file_name", type=click.Path(exists=True), default="topic_links_list.csv")
@click.argument("col_no", type=click.IntRange(min=0), default=0)
def run(single_keyword, file_name, col_no):
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
    process.crawl(EksiSimilarBaslikSpider, single_keyword=single_keyword, file_name=file_name, col_no=col_no)
    process.start()
