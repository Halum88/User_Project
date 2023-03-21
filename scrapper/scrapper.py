from fake_useragent import UserAgent
import requests
import random
import os
import psycopg2
from bs4 import BeautifulSoup
from requests import get
from threading import Timer


base_url = "https://www.1cont.ru/contragent/by-region"


def scrapper():
    scrapper.call_count += 1
    
    if scrapper.call_count > 5:
        print("Nope...")
        return
    
    try:
        response = get(base_url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        list = soup.find('div', class_='col-xs-12 col-sm-12 col-md-6 col-lg-4')
        ul = list.find('ul')
        for li in ul.find_all('li'):  
            a = li.find_all('a')
            region = a[0].text.strip()  #Регион
            link = li.find('a', href=True)['href']   #Ссылка
            # print(region, '-', base_url + link)

    except Exception as error:
        print('Error:', error)
        # Timer(4, scrapper).start()

scrapper.call_count = 0        

scrapper()