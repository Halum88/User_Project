from fake_useragent import UserAgent
import requests
import random
import os
import psycopg2
from bs4 import BeautifulSoup
from requests import get

test_url1="https://httpbin.org/user-agent"
test_url2="http://icanhazip.com"


base_url = "https://vypiska-nalog.com/reestr"
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


# def connect_site():
#     for i in range(5):
#         prox = session()
#         try:
#             connecting = get(test_url2, headers=headers, proxies=prox, timeout=1.5).text.strip()
#             return connecting
#         except Exception as error:
#             continue
        
# print(session())


def scrapper():
    for i in range(5):
        prox = session()
        print(prox)
        try:
            response = get(url=base_url, headers=headers, proxies=prox, timeout=1.5)
            soup = BeautifulSoup(response.text, 'html.parser')
            publication = soup.find_all('div', class_ = 'col-md-6').text.strip()   
            print(publication)
        except Exception as error:
            continue
    
        
        
###___main___###
# print(connect_site())
scrapper()