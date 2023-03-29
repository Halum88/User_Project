from fake_useragent import UserAgent
import requests
import random
import os
import psycopg2
from bs4 import BeautifulSoup
from requests import get
from threading import Timer


base_url = "https://www.1cont.ru/contragent/by-region"
db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
dict = []
ua = UserAgent()
headers = {'User-Agent': ua.random} #рандомный user-agent
dict_ok = []
max_id = 1
dict_reg = {}


###Рандомный прокси из БД###
def rand_proxi():     
    try:
        db = psycopg2.connect(
                    database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
                )   
        cursor = db.cursor() 
        cursor.execute('''SELECT host FROM proxy''')
        host = cursor.fetchall()
        for i in host:
            for j in i:
                dict.append(j)
        return dict
    except Exception as e:
        print('ERROR in DB - random proxies: ', e)
    finally:
        db.close()


###Получаем мксимальное значение id в БД###
def maxim_id():
    try:
        db = psycopg2.connect(
                database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
            )   
        cursor = db.cursor() 
        cursor.execute('select max(id) from users')
        
        global max_id
        max_id = cursor.fetchone()[0]
        if max_id is None:
            max_id = 0
    except Exception as e: 
        print("ERROR in DB - max id: ", e) 
    finally:
        db.close()  


###Все регионы из БД###
def region_id():
    try:
        db = psycopg2.connect(
                database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
            )   
        cursor = db.cursor() 
        cursor.execute('''SELECT id, name FROM region''')
        records = cursor.fetchall()
        for i in records:
            dict_reg[i[1]] = i[0]
        return dict_reg
    except Exception as error:   
         print("ERROR in DB - region id: ", error) 
    finally:
        db.close() 


###Создаем сессию###
def session():
        prx = rand_proxi()
        proxi = random.choice(prx)
        return proxi


def scrapper(base_url):
    global max_id
    global dict_reg
    scrapper.call_count += 1
    count = 0
    if scrapper.call_count > 50:
        print("Nope...")
        return
    
    
    db = psycopg2.connect(
                database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
            )   
    cursor = db.cursor() 
    
    
    proxi = session()
    proxis = {"http://": proxi, "https://": proxi}
    try:
        response = get(base_url, headers=headers, proxies=proxis, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        reg_list = soup.find_all('a', class_='contragent-link')
        for reg in reg_list:
            region = reg.text   #Регионы
            link = reg['href']   #Ссылки регионов
            
            ###Запись регионов в бд###
            if len(dict_reg) == 0 or region not in dict_reg:
                cursor.execute('''INSERT INTO region(id, name, link) VALUES(%s, %s,%s)
                               ON CONFLICT (link)
                               DO NOTHING
                               RETURNING id''',(None, region, link))
                id_db = cursor.fetchone()
                dict_reg[region] = id_db[0]

   
    
    
    
    
    
        db.commit()
        db.close() 
        
    except Exception as error:
        print('Error:',proxi,'---', error)
        # Timer(4, scrapper).start()

    
scrapper.call_count = 0


###___main___###

region_id()
scrapper(base_url)