from fake_useragent import UserAgent
import requests
import random
import os
import psycopg2
from bs4 import BeautifulSoup
from requests import get
from threading import Timer

# https://www.1cont.ru/contragent?page=
base_url = "https://www.1cont.ru/contragent?page="
db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
dict = []
ua = UserAgent()
headers = {'User-Agent': ua.random} #рандомный user-agent
dict_ok = []
max_id = 1


###Количество обрабатываемых страниц###
def page_proccessing(link):
    for page in range(1,5):
        scrapper(link,page)


###Рандомный прокси из БД###
def rand_proxi():     
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
    except Exception as error: 
         print("DB error", error) 
    finally:
        db.close()  


###Создаем сессию###
def session():
        prx = rand_proxi()
        proxi = random.choice(prx)
        return proxi


def scrapper(base_url, page):
    global max_id
    scrapper.call_count += 1
    count = 0
    if scrapper.call_count > 50:
        print("Nope...")
        return
    
    db = psycopg2.connect(
                database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
            )   
    cursor = db.cursor() 
    
    url = base_url + str(page)
    proxi = session()
    proxis = {"http://": proxi, "https://": proxi}
    try:
        response = get(url, headers=headers, proxies=proxis, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        tbody = soup.find_all('div', class_='tr tbody-tr')
        
        for list in tbody:
            count += 1
            name = list.find('div', class_='td').find('a').text   #Имя
            status = list.find('div', class_='td__text').text   #Статус
            ogrn = list.find_all('div', class_='td__text')[1].text   #ОГРН
            inn = list.find_all('div', class_='td__text')[2].text   #ИНН
            activity = list.find_all('div', class_='td__text')[3].text   #ОКВЭД
            date_registr = list.find_all('div', class_='td__text')[4].text   #Дата регистрации    
            
            if status == 'Действует' and count < 150:     
                max_id += 1
                cursor.execute(('''INSERT INTO users(id,name,status,inn,ogrn,activity,date) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (inn)
                                DO UPDATE
                                SET name=%s, status=%s, ogrn=%s,activity=%s,date=%s
                                '''),[max_id,name,status,int(inn),int(ogrn),activity,date_registr,name,status,int(ogrn),activity,date_registr])
                       
        db.commit()
        db.close()
        
    except Exception as error:
        print('Error:',proxi,'---', error)
        # Timer(4, scrapper).start()

    
scrapper.call_count = 0


###___main___###
page_proccessing(base_url)
