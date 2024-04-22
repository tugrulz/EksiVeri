import sys

import click
import requests as rq
import pandas as pd
import re
import concurrent.futures
from bs4 import BeautifulSoup



def get_entry_ids(path, nrows, col_name):
    df = pd.read_csv(usecols = [col_name], filepath_or_buffer = path, nrows = nrows )
    return df[col_name].tolist()

def parse_response(response):
    """Implemented using regular expressions. Implementation is dependent on some formatting details of response"""
    return re.findall('@[^<]*(?=<)', response)






caylak_responses = []
responses = []

headers = {"authority": "eksisozluk.com",
               "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
               "x-requested-with": "XMLHttpRequest"}

session = rq.Session()
login_response = session.get("https://eksisozluk.com/giris", headers = headers)
soup = BeautifulSoup(login_response.text, features="html.parser")
token = soup.find("input", attrs={"name": "__RequestVerificationToken"}).attrs["value"]
session.post("https://eksisozluk.com/giris", data=dict(
    UserName="copikifrankmis@gmail.com",
    Password="Tugrulcan!4!",
    RememberMe="false",
    __RequestVerificationToken=token

), headers=headers)

def send_request(entry_id):

    url = "https://eksisozluk.com/entry/favorileyenler?entryId=" + str(entry_id)
    caylak_url = "https://eksisozluk.com/entry/caylakfavorites?entryid=" + str(entry_id)

    headers["path"] = "/entry/favorileyenler?entryId=" + str(entry_id)

    response = session.get(url, headers=headers)

    headers["path"] = "/entry/caylakfavorites?entryid=%" + str(entry_id)

    caylak_response = session.get(caylak_url, headers=headers)

    return [response.text, caylak_response.text]

def send_concurrent_requests(num_of_threads, entry_ids):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_threads) as executor:
        for entry_id, result in zip(entry_ids, executor.map(send_request, entry_ids[0:20])):
            result = [parse_response(s) for s in result]
            result = {entry_id: result}
            results.append(result)
        return results

@click.command()
@click.option('--max_threads', default=10, show_default=True, help="Maximum number of threads to use. Optimal value might change from system to system.")
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path',type=click.Path(file_okay=True))
@click.argument('entry_id_column_name')
def scrape_favorites(max_threads, input_path, output_path, entry_id_column_name):
    entry_ids = get_entry_ids(input_path, 9999, entry_id_column_name)
    data = send_concurrent_requests(max_threads, entry_ids)
    print(data)
    df = pd.DataFrame(data=data, columns=["title", "entry", "author", "date_time", "entry_id"])
    df.to_csv(output_path, index=False)

