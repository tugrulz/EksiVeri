import re

import click
import requests as rq
from bs4 import BeautifulSoup
import pandas as pd

from datetime import datetime, timedelta

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def get_single_date(date):
    url = "https://sozlock.com/?date=" + date.strftime("%Y-%m-%d")
    response = rq.get(url)
    soup = BeautifulSoup(response.text, features="html.parser")
    results = []
    for li in soup.find("ul", attrs={"class":"listnone entrylist"}).findAll("li"):
        results.append((get_title(li), get_entry_text(li), get_author(li), get_datetime(li), get_entryid(li)))
    return results

def get_entryid(li):
    return re.findall("[0-9]+", li.find("a", attrs={"title": "orjinalini gör"}).attrs["href"])[0]


def get_datetime(li):
    return li.find("span", attrs={"class": "entrytime small"}).text


def get_author(li):
    return li.find("a", attrs={"class": "yazar"}).text


def get_entry_text(li):
    return li.find("p").text


def get_title(li):
    return li.h3.text


def get_debe(start_date, end_date):


    results = []

    for date in daterange(start_date, end_date):
        result = get_single_date(date)
        results.extend(result)
    return results

@click.command()
@click.argument('start_date', type=click.DateTime(formats=("%d.%m.%Y","%d-%m-%Y")))
@click.argument('end_date', type=click.DateTime(formats=("%d.%m.%Y","%d-%m-%Y")))
@click.argument('output_path',type=click.Path(file_okay=True))
def scrape_debe(start_date, end_date, output_path):
    data = get_debe(start_date, end_date)
    df = pd.DataFrame(data=data, columns=["title", "entry", "author", "date_time", "entry_id"])
    df.to_csv(output_path, index=False)

