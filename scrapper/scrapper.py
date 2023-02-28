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
proxy_dict = []
max_id = 1

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


def id_max():
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
        raise Exception('Nо connect to DB!', error) 
    finally:
        db.close()

 
    
def scrap_proxy():
    response = get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxy_list = soup.find('table', class_ = 'table table-striped table-bordered').find_all('tr')[1:]
    global proxy_dict
    global max_id
    
    ###Подключаемся к БД###
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
        
    
    ###Получаем список хостов###
    for host_list in proxy_list:
        tds = host_list.find_all('td')
        ip = tds[0].text.strip()
        port = tds[1].text.strip()
        host = f"{ip}:{port}"
        proxy_dict.append(host)


        ###Проверка на дубли хостов###
        try:
            if len(proxy_dict) == 0 or host not in proxy_dict:
                cursor.execute('''INSERT INTO proxy(id, host) VALUES (%s,%s) 
                                RETURNING id''',(None, str(host)))
                ip_db = cursor.fetchone()
                proxy_dict[host] = ip_db[0]
        except Exception as error:
            print('DB error', error)
        
        
    ###Запись хостов в БД###
    for hosts in proxy_dict:    
        try:
            max_id += 1
            cursor.execute('''INSERT INTO proxy VALUES (%s,%s) 
                              ON CONFLICT (host) DO UPDATE 
                              SET host=%s
                              ''',[max_id, hosts, hosts])
        
        except Exception as error:
            raise Exception('Recording error', error)
            
    db.commit()
    db.close()
    time.sleep(1 + (random.random() * (9 - 5)))

        # proxy_random = random.choice(proxy_dict)    # рандом прокси
    


# def test():
#     db = db = psycopg2.connect(
#             database = db_name, 
#             user = user_name, 
#             password = user_pw, 
#             host="127.0.0.1", 
#             port="5432"
#             )
#     cursor = db.cursor()
#     cursor.execute('''SELECT * FROM proxy order by id''')
#     test = cursor.fetchall()
#     print(*test)


###___main___###
init_db()
id_max()
scrap_proxy()
# test()
