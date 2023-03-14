import os
import requests
import random
import psycopg2
import time
from requests import get
from bs4 import BeautifulSoup


base_url = 'https://free-proxy-list.net/'
db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
proxy_dict = []
max_id = 1
proxy_db = []


###Инициализая БД###
def init_db():
    try:
        db = psycopg2.connect(
        database = db_name, 
        user = user_name, 
        password = user_pw, 
        host="127.0.0.1", 
        port="5432"
        )   
    except Exception as error:
        raise Exception('Nо connect to DB!', error)
    finally:
        db.close()


def maxim_id():
    try:
        db = psycopg2.connect(
        database = db_name, 
        user = user_name, 
        password = user_pw, 
        host="127.0.0.1", 
        port="5432"
        )
        global max_id
        cursor = db.cursor()
        cursor.execute('''SELECT max(id) FROM proxy''')
        max_id = cursor.fetchone()[0]
        if max_id is None:
            max_id = 0 
            
    except Exception as error:
        raise Exception('Nо max(id) to DB!', error) 
    finally:
        db.close()

 
def scrap_proxy():
    response = get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxy_list = soup.find('table', class_ = 'table table-striped table-bordered').find_all('tr')[1:]
    global proxy_dict
    
    
    ###Получаем список хостов###
    for host_list in proxy_list:
        tds = host_list.find_all('td')
        ip = tds[0].text.strip()
        port = tds[1].text.strip()
        host = f"{ip}:{port}"
        proxy_dict.append(host)
        
    time.sleep(1 + (random.random() * (9 - 5)))


def check_proxy():
    global max_id
    try:
        db = psycopg2.connect(
            database = db_name, 
            user = user_name, 
            password = user_pw, 
            host="127.0.0.1", 
            port="5432"
            )
        cursor = db.cursor()     
    except Exception as error:
        raise Exception('Not connect DB', error)
    
    for px in proxy_dict:
        proxies = {"http": px, "https": px}
        try:
            get('http://icanhazip.com', proxies=proxies, timeout=0.9).text.strip()
            try:
                max_id += 1
                cursor.execute('''INSERT INTO proxy VALUES (%s,%s) 
                                ON CONFLICT (host) DO UPDATE 
                                SET host=%s
                                ''',[max_id, px, px])
            except Exception as error:
                raise Exception('Recording error', error)
        except Exception as e:
           proxy_dict.remove(px)
           
    
    db.commit()
    db.close()


###___main___###
init_db()
maxim_id()
scrap_proxy()
check_proxy()
