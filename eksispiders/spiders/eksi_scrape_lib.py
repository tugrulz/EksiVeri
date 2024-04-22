import os
import csv
import selector_constants as sel_cons

def parse_date(entry_date):
    date = ""
    edit_date = ""
    if '~' in entry_date:
        entry_date_split = entry_date.split("~")
        first_date = (entry_date_split[0].strip()).split(" ")
        second_date = (entry_date_split[1].strip()).split(" ")
        if len(first_date) == 2 and len(second_date) == 2:
            date1 = first_date[0].split(".")
            date2 = second_date[0].split(".")
            date = date1[2] + "-" + date1[1] + "-" + date1[0] + " " + first_date[1] + ":00"
            edit_date = date2[2] + "-" + date2[1] + "-" + date2[0] + " " + second_date[1] + ":00"
        elif len(first_date) == 2 and len(second_date) == 1:
            date1 = first_date[0].split(".")
            date = date1[2] + "-" + date1[1] + "-" + date1[0] + " " + first_date[1] + ":00"
            edit_date = date1[2] + "-" + date1[1] + "-" + date1[0] + " " + second_date[0] + ":00"
        elif len(first_date) == 1 and len(second_date) == 2:
            date1 = first_date[0].split(".")
            date2 = second_date[0].split(".")
            date = date1[2] + "-" + date1[1] + "-" + date1[0] + " " + "00:00:00"
            edit_date = date2[2] + "-" + date2[1] + "-" + date2[0] + " " + second_date[1] + ":00"
        else:
            date1 = first_date[0].split(".")
            date2 = second_date[0].split(".")
            date = date1[2] + "-" + date1[1] + "-" + date1[0] + " " + "00:00:00"
            edit_date = date2[2] + "-" + date2[1] + "-" + date2[0] + " " + "00:00:00"
    else:
        entry_date_split = entry_date.split(" ")
        date1 = entry_date_split[0].split(".")
        if len(entry_date_split) == 2:
            date = date1[2] + "-" + date1[1] + "-" + date1[0] + " " + entry_date_split[1] + ":00"
        else:
            date = date1[2] + "-" + date1[1] + "-" + date1[0] + " " + "00:00:00"
    return date, edit_date

def create_int_output_files():
    if not os.path.exists('data'):
        os.mkdir('data')
    absolute_path = 'data/'
    if not os.path.exists(absolute_path + '404_topic.csv'):
        with open(absolute_path + '404_topic.csv', encoding = 'utf-8', mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['topic'])
    if not os.path.exists(absolute_path + '404_topic_link.csv'):
        with open(absolute_path + '404_topic_link.csv', encoding = 'utf-8', mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['topic_link'])
    if not os.path.exists(absolute_path + 'remaining_topics.csv'):        
        with open( absolute_path + 'remaining_topics.csv', encoding = 'utf-8', mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['503_errors'])  

def parse_single_entry(response, content_limit, def_file, long_file, link_file):
    topic_name = response.css(sel_cons.TOPIC_NAME_SELECTOR).extract_first()
    entry_block = response.css(sel_cons.SET_SELECTOR)
    entry_id = entry_block.css(sel_cons.ENTRY_ID_SELECTOR).extract_first()
    content_list = entry_block.css(sel_cons.ENTRY_SELECTOR).extract()
    entry_date = entry_block.css(sel_cons.ENTRY_DATE_SELECTOR).extract_first()
    fav_num = entry_block.css(sel_cons.FAV_NUM_SELECTOR).extract_first()
    link_list = entry_block.css(sel_cons.LINK_SELECTOR)
    for l in link_list:
        link = l.css("::attr(href)").extract_first()
        if link.startswith('/'):
            link = 'https://eksisozluk.com' + link
        text = l.css("::text").extract_first()
        if not text:
            text = ""
        with open( link_file, encoding = 'utf-8', mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([topic_name, entry_id, link, text])
    if not fav_num:
        fav_num = '0'
    content = ""
    for x in content_list:
        x = x.replace("\r"," ")
        x = x.replace("\n"," ")
        x = x.strip()
        content += x + ' ' 
    author = entry_block.css(sel_cons.WRITER_SELECTOR).extract_first()
    amateur = entry_block.css(sel_cons.AMATEUR_WRITER_SELECTOR).extract_first()
    entry = []
    long_entry = []
    entry.append(topic_name)
    entry.append(entry_id)
    entry.append(author)
    if amateur:
        entry.append("true")
    else:
        entry.append("false")
    date, edit_date = parse_date(entry_date)
    entry.append(date)
    entry.append(edit_date)   
    entry.append(fav_num)
    entry.append(content[:content_limit])
    long_entry.append(topic_name)
    long_entry.append(entry_id)
    long_entry.append(content)
    with open(long_file, encoding = 'utf-8', mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(long_entry)
    with open(def_file, encoding = 'utf-8', mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(entry)

def parse_topic_entry(response, content_limit, def_file, long_file, link_file):
    topic_name = response.css(sel_cons.TOPIC_NAME_SELECTOR).extract_first()
    #tam olarak anlayamadigim bir nedenden oturu pager'in icinin bos oldugunu dusunuyor ondan linkleri alamiyoruz
    current_page = response.css(sel_cons.CURRENT_PAGE_SELECTOR).extract_first()
    for index, entry_block in enumerate(response.css(sel_cons.SET_SELECTOR), start=1):
        entry_id = entry_block.css(sel_cons.ENTRY_ID_SELECTOR).extract_first()
        content_list = entry_block.css(sel_cons.ENTRY_SELECTOR).extract()
        entry_date = entry_block.css(sel_cons.ENTRY_DATE_SELECTOR).extract_first()
        fav_num = entry_block.css(sel_cons.FAV_NUM_SELECTOR).extract_first()
        link_list = entry_block.css(sel_cons.LINK_SELECTOR)
        for l in link_list:
            link = l.css("::attr(href)").extract_first()
            if link.startswith('/'):
                link = 'https://eksisozluk.com' + link
            text = l.css("::text").extract_first()
            if not text:
                text = ""
            with open( link_file, encoding = 'utf-8', mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([topic_name, entry_id, link, text])
        if not fav_num:
            fav_num = '0'
        content = ""
        for x in content_list:
            x = x.replace("\r"," ")
            x = x.replace("\n"," ")
            x = x.strip()
            content += x + ' '
        author = entry_block.css(sel_cons.WRITER_SELECTOR).extract_first()
        entry = []
        long_entry = []
        entry.append(topic_name)
        entry.append(entry_id)
        entry.append(author)
        date, edit_date = parse_date(entry_date)
        entry.append(date)
        entry.append(edit_date)
        entry.append(fav_num)
        entry.append(content[:content_limit])
        if current_page:
            entry.append(str(index + 10 * (int(current_page) - 1)))
        else:
            entry.append(index)
        long_entry.append(topic_name)
        long_entry.append(entry_id)
        long_entry.append(content)
        with open(long_file, encoding = 'utf-8', mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(long_entry)
        with open(def_file, encoding = 'utf-8', mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(entry)