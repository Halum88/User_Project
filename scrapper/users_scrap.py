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
dict_ok = []

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
        return proxi


def scrapper():
    scrapper.call_count += 1
    count = 0
    if scrapper.call_count > 50:
        print("Nope...")
        return
    
    proxi = session()
    proxis = {"http": proxi, "https": proxi}
    try:
        response = get(base_url, headers=headers, proxies=proxis, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        list = soup.find('div', class_='col-xs-12 col-sm-12 col-md-6 col-lg-4')
        ul = list.find('ul')
        for li in ul.find_all('li'):  
            a = li.find_all('a')
            region = a[0].text.strip()  #Регион
            link = li.find('a', href=True)['href']   #Ссылка
            count+=1
            print(region, '-', base_url + link)
        
        db = psycopg2.connect(database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
            )
        cursor = db.cursor()  
        cursor.execute(('''INSERT INTO proxies_ok(host)
                               VALUES (%s)
                               ON CONFLICT (host)
                               DO NOTHING'''),[str(proxi)])  
        db.commit()
        db.close()
        print(proxi)
                
        Timer(4, scrapper).start()
    except Exception as error:
        print('Error:',proxi,'---', error)
        Timer(4, scrapper).start()

#  {'http': '144.76.60.58:8118', 'https': '144.76.60.58:8118'}    
# {'http': '162.55.188.41:8020', 'https': '162.55.188.41:8020'}   
# {'http': '8.219.176.202:8080', 'https': '8.219.176.202:8080'}
# 91.106.65.107:9812
# 200.105.215.22:33630
scrapper.call_count = 0
###___main___###
scrapper()
