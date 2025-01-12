import os
import requests
import random
import psycopg2
from datetime import datetime
from requests import get
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dotenv import load_dotenv
import logging


load_dotenv()


# логгирование
div_log = 'prx_scrapper/logs_prx/'
log_file = f'proxy_{datetime.now().strftime("%d_%m_%Y")}.log'
logging.basicConfig(filename=div_log + log_file, level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')



proxy_url = os.environ['PROXY_URL']
db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']
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
            database = db_name, user = user_name, password = user_pw, host=db_host, port=db_port
        )
        logging.info('Connect to DB')   
    except Exception as error:
        raise Exception('Nо connect to DB!', error)
    finally:
        db.close()


def maxim_id():
    global max_id
    try:
        db = psycopg2.connect(
            database = db_name, user = user_name, password = user_pw, host=db_host, port=db_port
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
    response = get(proxy_url)
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
            response = requests.get(f'{proxy_url}', headers=headers, proxies={'https://':i,'http://':i}, timeout=5)
            if response.status_code == 200:
                count_1 += 1  
                proxy_dict.append(i) 
            else:
                print('connect: NOT OK')
        print('proxies получено:', count_1)
        logging.info('proxies получено: %s', count_1)
    except Exception as e:
        print('ERROR connect:', e)


def rec_db():
    global max_id
    try:
        db = psycopg2.connect(
            database = db_name, user = user_name, password = user_pw, host=db_host, port=db_port
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
        logging.info('insert to DB')
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