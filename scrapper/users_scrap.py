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
    proxy_random = random.choice(host)
    for pxy in proxy_random:
        return pxy
    

proxy = rand_proxy()
print(proxy)

# def get_session(proxies):
#     # создать HTTP‑сеанс
#     session = requests.Session()
#     # выбираем один случайный прокси
#     proxy = random.choice(proxies)
#     session.proxies = {"http": proxy, "https": proxy}
#     return session



# for i in range(5):
#     s = get_session(proxies)
#     try:
#         print("Страница запроса с IP:", s.get("http://icanhazip.com", timeout=1.5).text.strip())
#     except Exception as e:
#         continue