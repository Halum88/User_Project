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


count = 0
max_id = 1
proxy_dict = []
proxies_https = []
proxies_http = []

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
                if count <= 50:
                    td = tr.find_all('td')
                    ip = td[0].text.strip()
                    port = td[1].text.strip()
                    protocol = td[6].text.strip().lower()
                    if protocol == 'yes':
                        proxies_https.append(f"https://{ip}:{port}")
                    elif protocol == 'no':
                        proxies_http.append(f"http://{ip}:{port}")            
    except Exception as e:
        raise Exception("Error:", response.status_code)


def check():
    c1 = 0
    c2 = 0
    try:
        for i in proxies_https:
            c1 += 1
            response = requests.get("https://www.google.com", proxies={'https://':i}, timeout=5)
            if response.status_code == 200:
                print('https: OK', c1, i)
            else:
                print('https: NOT OK')
    except Exception as e:
        print('ERROR:', e)

    try:
        for i in proxies_http:
            c2 += 1
            response = requests.get("https://www.google.com", proxies={'http://':i}, timeout=5)
            if response.status_code == 200:
                print('http: OK', c2, i)
            else:
                print('http: NOT OK')
    except Exception as e:
        print('ERROR:', e)


###___main___###
init_db()
maxim_id()
scrap_proxy()
check()