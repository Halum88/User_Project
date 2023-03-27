import os
import requests
import random
import psycopg2
import time
from requests import get
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


base_url = 'https://free-proxy-list.net/'
db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
ua = UserAgent()
headers = {'User-Agent': ua.random} #рандомный user-agent


count = 0
count_1 = 0
count_2 = 0
max_id = 1
proxy_dict = []
prx_list = []

###Инициализая БД###
def init_db():
    try:
        db = psycopg2.connect(
            database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
        )   
    except Exception as error:
        raise Exception('Nо connect to DB!', error)
    finally:
        db.close()


def maxim_id():
    global max_id
    try:
        db = psycopg2.connect(
            database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
        )   
        cursor = db.cursor()
        cursor.execute('''SELECT max(id) FROM proxy''')
        max_id = cursor.fetchone()[0]
        if max_id is None:
            max_id = 0 
        return max_id
  
    except Exception as error:
        raise Exception('Nо max(id) to DB!', error) 
    finally:
        db.close()

 
def scrap_proxy():
    global count
    response = get(base_url)
    try:
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', attrs={'class': 'table table-striped table-bordered'})
            tbody = table.find('tbody')
            
            for tr in tbody.find_all('tr'):
                count += 1
                if count <= 30:
                    td = tr.find_all('td')
                    ip = td[0].text.strip()
                    port = td[1].text.strip()
                    prx_list.append(f"{ip}:{port}")
         
    except Exception as e:
        raise Exception("Error:", response.status_code)


def check():
    global count_1
    global proxy_dict
    try:
        for i in prx_list:
            response = requests.get("https://www.1cont.ru/contragent/by-region", headers=headers, proxies={'https://':i,'http://':i}, timeout=5)
            if response.status_code == 200:
                count_1 += 1  
                proxy_dict.append(i) 
            else:
                print('connect: NOT OK')
        print('proxies получено:', count_1)
    except Exception as e:
        print('ERROR connect:', e)


def rec_db():
    global max_id
    try:
        db = psycopg2.connect(
            database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
        )   
        cursor = db.cursor()
        for px in proxy_dict:
            max_id += 1
            cursor.execute(('''INSERT INTO proxy(id, host)
                               VALUES (%s,%s)
                               ON CONFLICT (host)
                               DO UPDATE
                               SET id=%s
                            '''),[max_id, px, max_id])
    except Exception as e:
        raise e
    
    db.commit()
    db.close()
    
    
###___main___###
init_db()
maxim_id()
scrap_proxy()
check()
rec_db()