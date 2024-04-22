import os
from enum import Enum
import requests as rq
from bs4 import BeautifulSoup
import concurrent.futures
import pandas as pd
import re
import click

short_entry_n = 280


class AuthorStatus(Enum):
    EXISTS = 1
    LEYLA = 2
    DOES_NOT_EXIST = 3


max_num_of_threads = 5

headers = {"authority": "eksisozluk.com",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/81.0.4044.138 Safari/537.36",
           "x-requested-with": "XMLHttpRequest"}

session = rq.Session()
login_response = session.get("https://eksisozluk.com/giris", headers=headers)
soup = BeautifulSoup(login_response.text, features="html.parser")
token = soup.find("input", attrs={"name": "__RequestVerificationToken"}).attrs["value"]
session.post("https://eksisozluk.com/giris", data=dict(
    UserName="copikifrankmis@gmail.com",
    Password="Tugrulcan!4!",
    RememberMe="false",
    __RequestVerificationToken=token

), headers=headers)


def get_entry_content(tag):
    return tag.find("div", attrs={"class": "content"}).text.strip()


def get_entryid(tag):
    return re.findall("[0-9]+", tag.find("a", attrs={"class": "entry-date permalink"}).attrs["href"])[0]


def get_datetime(tag):
    return tag.find("a", attrs={"class": "entry-date permalink"}).text


def get_title(tag):
    return tag.find("span", attrs={"itemprop": "name"}).text


def get_entry_author(tag):
    return tag.find("a", attrs={"class": "entry-author"}).text


def author_status(author):
    url = "https://eksisozluk.com/biri/" + str(author)
    response = session.get(url, headers=headers)
    if (response.status_code != 200):
        return AuthorStatus.DOES_NOT_EXIST
    soup = BeautifulSoup(response.text, features="html.parser")
    element = soup.find("div", attrs={"class": "tabs-content", "id": "profile-stats-section-content"})
    if (element.text == "yok ki öyle bişey"):
        return AuthorStatus.LEYLA
    else:
        return AuthorStatus.EXISTS


def log_non_existing_author(author, status, output_folder):
    df = pd.DataFrame({"author": [author], "status": [status]})
    df.to_csv(output_folder + "/problematic_authors.csv", index=False, mode="a")


def send_request(author, output_folder):
    # open folder for the author if the author exists
    if author_status(author) == AuthorStatus.EXISTS:
        if not os.path.isdir(
                output_folder + "/" + author + "/"):  # if the folder does not exist already create the folder
            os.makedirs(os.path.dirname(output_folder + "/" + author + "/"), exist_ok=False)
    else:
        log_non_existing_author(author, author_status(author), output_folder)
        return

    num_of_entries, twitter_handle = get_author_details(author)
    print(num_of_entries, twitter_handle)

    channels = get_channels(author)
    df = pd.DataFrame(data=channels, columns=["channel", "number_of_entries"])
    df.to_csv(output_folder + "/" + author + "/channels.csv", index=False)

    favs = get_favorite_authors(author)
    df = pd.DataFrame(data=favs, columns=["author", "rank"])
    df.to_csv(output_folder + "/" + author + "/favorite_authors.csv", index=False)

    entries = get_author_entries(author, num_of_entries)
    df = pd.DataFrame(data=entries, columns=["author", "entry_short", "entry_id", "datetime", "title"])
    df.to_csv(output_folder + "/" + author + "/author_entries.csv", index=False)

    entries = get_author_favorites(author, num_of_entries)
    df = pd.DataFrame(data=entries, columns=["author", "entry_author", "entry_short", "entry_id", "datetime", "title"])
    df.to_csv(output_folder + "/" + author + "/author_fav_entries.csv", index=False)


def get_favorite_authors(author):
    url = "https://eksisozluk.com/favori-yazarlari?nick=" + str(author)
    response = session.get(url, headers=headers)
    response.status_code
    soup = BeautifulSoup(response.text, features="html.parser")
    table = soup.find_all("tr")
    return [(x.td.a.text.strip(), i) for x, i in zip(table, range(1, len(table) + 1))]


def send_author_entry_page_request(author, page_num):
    author_entries_url = "https://eksisozluk.com/son-entryleri?nick=" + str(author) + "&p=" + str(page_num)
    response = session.get(author_entries_url, headers=headers)
    print("page: ", page_num, response.status_code)
    return response


def send_author_favorite_page_request(author, page_num):
    author_entries_url = "https://eksisozluk.com/favori-entryleri?nick=" + str(author) + "&p=" + str(page_num)
    return session.get(author_entries_url, headers=headers)


def get_author_entries(author, num_of_entries, num_of_threads=max_num_of_threads):
    results = []
    max_page_num = int(int(num_of_entries) / 10) + 1
    print(max_page_num)
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_threads) as executor:
        for result in executor.map(send_author_entry_page_request, [author for i in range(1, max_page_num)],
                                   range(1, max_page_num)):
            soup = BeautifulSoup(result.text, features="html.parser")
            result = [
                (author, get_entry_content(tag)[0:short_entry_n], get_entryid(tag), get_datetime(tag), get_title(tag))
                for tag in
                soup.findAll("div", attrs={"class": "topic-item"})]
            results.extend(result)
    return results


def get_author_favorites(author, num_of_entries, num_of_threads=max_num_of_threads):
    results = []
    max_page_num = int(int(num_of_entries) / 10) + 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_threads) as executor:
        for result in executor.map(send_author_favorite_page_request, [author for i in range(1, max_page_num)],
                                   range(1, max_page_num)):
            soup = BeautifulSoup(result.text, features="html.parser")
            result = [(author, get_entry_author(tag), get_entry_content(tag)[0:short_entry_n], get_entryid(tag),
                       get_datetime(tag), get_title(tag)) for tag in
                      soup.findAll("div", attrs={"class": "topic-item"})]
            results.extend(result)
    return results


def get_channels(author):
    channels_url = "https://eksisozluk.com/katkida-bulundugu-kanallar?nick=" + str(author)
    response = session.get(channels_url, headers=headers)
    soup = BeautifulSoup(response.text, features="html.parser")
    return [(x.td.a.text, x.td.span.text) for x in soup.find_all("tr")]


def get_author_details(author):
    url = "https://eksisozluk.com/biri/" + str(author)
    response = session.get(url, headers=headers)
    print("response code: " + str(response.status_code))
    soup = BeautifulSoup(response.text, features="html.parser")
    num_of_entries = soup.find(title="toplam entry sayısı").text

    twitter_tag = soup.find("a", attrs={"class": "twitter-timeline"})
    if (twitter_tag != None):
        twitter_handle = twitter_tag.attrs["data-screen-name"]
    else:
        twitter_handle = "-"
    return num_of_entries, twitter_handle


@click.command()
@click.option('--nrows', default=-1, show_default=True,
              help="Only scrape the first nrow many authors. Reads all the authors in the input file if -1 or unspecified")
@click.argument('input_csv', type=click.Path(exists=True))
@click.argument('output_folder', type=click.Path(dir_okay=True))
@click.argument('author_column_name')
@click.argument('entry_crop_lenght', type=click.IntRange(min=0))
def scrape_authors_from_csv(nrows, input_csv, output_folder, author_column_name, entry_crop_length):
    nonlocal short_entry_n
    short_entry_n = entry_crop_length
    df = pd.DataFrame()
    if (nrows == -1):
        df = pd.read_csv(input_csv, usecols=[author_column_name])
    else:
        df = pd.read_csv(input_csv, usecols=[author_column_name], nrows=nrows)
    for author in df[author_column_name]:
        print(author)
        send_request(author, output_folder)
