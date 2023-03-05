from fake_useragent import UserAgent
import requests
import random
import os
import psycopg2


ua = UserAgent()
url = 'https://httpbin.org/user-agent'

db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
dict = []
headers = {'User-Agent': ua.random}

result = requests.get(url, headers=headers)
# print(result.content)

###Рандомный прокси из БД###
def rand_proxy():     
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
   

def session():
        prx = rand_proxy()
        session = requests.Session()
        proxy = random.choice(prx)
        session.proxies = {"http": proxy, "https": proxy}
        return session


def start():
    for i in range(5):
        s = session()
        try:
            print("Страница запроса с IP:", s.get("http://icanhazip.com", timeout=1.5).text.strip())
        except Exception as error:
            continue

start()