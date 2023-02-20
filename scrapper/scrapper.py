import os
from bs4 import BeautifulSoup
from requests import get
import re


base_url = 'https://free-proxy-list.net/'
count = 0
dict = []
#def init_db():


def scrapping():
    response = get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxy_list = soup.find('div', class_ = 'table-responsive fpl-list')
    global count
    global dict

    try:
        for all_proxy in proxy_list:
            tr = all_proxy.find_all('tr')
            for j in tr:
                td = j.find('td')
                ip = re.sub('<[^>]+>',"",str(td))
                dict.append(ip)              
    
    except Exception as error:
        return error






#___main___#

scrapping()

