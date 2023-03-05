from fake_useragent import UserAgent
import requests
import random
import os
import psycopg2


test_url1="https://httpbin.org/user-agent"
test_url2="http://icanhazip.com"


url = "https://vypiska-nalog.com/reestr"
db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
dict = []
ua = UserAgent()
headers = {'User-Agent': ua.random} #рандомный user-agent


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
   
###Создаем сессию###
def session():
        prx = rand_proxy()
        session = requests.Session()
        proxy = random.choice(prx)
        session.proxies = {"http": proxy, "https": proxy}
        return session


def connect_site():
    for i in range(5):
        ses = session()
        try:
            print('TEST: ', ses.get(test_url2, headers=headers, timeout=1.5).text.strip())
        except Exception as error:
            continue
        
        
        
###___main___###
connect_site()