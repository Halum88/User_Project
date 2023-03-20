from fake_useragent import UserAgent
import requests
import random
import os
import psycopg2
from bs4 import BeautifulSoup
from requests import get
from threading import Timer

test_url2="http://icanhazip.com"
base_url = "https://www.1cont.ru/contragent/by-region"
db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
dict = []
ua = UserAgent()
headers = {'User-Agent': ua.random} #рандомный user-agent


###Рандомный прокси из БД###
def rand_proxi():     
    db = psycopg2.connect(
            database = db_name, 
            user = user_name, 
            password = user_pw, 
            host="127.0.0.1", 
            port="5432"
            )
    cursor = db.cursor()
    cursor.execute('''SELECT host FROM proxy''')
    host = cursor.fetchall()
    for i in host:
        for j in i:
            dict.append(j)
    return dict


###Создаем сессию###
def session():
        prx = rand_proxi()
        proxi = random.choice(prx)
        proxies = {"http": proxi, "https": proxi}
        return proxies


def scrapper():
    scrapper.call_count += 1
    
    if scrapper.call_count > 10:
        print("Nope...")
        return
    
    prox = session()
    try:
        response = get(test_url2, headers=headers, proxies=prox, verify=False, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        # publication = soup.find('div', class_ = 'row').text.strip()
        # print(publication)
        print(response.text.strip)
        
    except Exception as error:
        print('Error:', error)
        Timer(4, scrapper).start()

        
scrapper.call_count = 0
###___main___###
scrapper()