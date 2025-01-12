from fake_useragent import UserAgent
import random
import os
import psycopg2
from bs4 import BeautifulSoup
from requests import get
from threading import Timer
from dotenv import load_dotenv
from psycopg2.extras import DictCursor
from get_region import get_region_in_db, rand_proxi, connect_db

load_dotenv()

url = os.environ['URL_SCRAPP']
base_url = os.environ['BASE_URL']
db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']




def get_users(region_id):
    proxis = {"http://": rand_proxi(), "https://": rand_proxi()}
    headers = {'User-Agent': UserAgent().random}
    
    url_reg = base_url+get_region_in_db(region_id)


    response = get(url_reg, headers=headers, proxies=proxis, timeout=5)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    current_page = 1
    users = []
    count = 0

    while True: 
        try:
            url = f"{url_reg}?page={current_page}"
            response = get(url, headers=headers, proxies=proxis, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')

            user_i = soup.find_all('div', class_='tr tbody-tr')

            for user in user_i:
                name = user.find('div', class_='td').find('a').text.strip()  # Имя пользователя
                count += 1
                users.append(name)

            next_page = soup.find('li', class_='PagedList-skipToNext')
            if next_page and 'disabled' not in next_page.get('class', []):  # Проверяем, активна ли кнопка "Next"
                current_page += 1  # Переходим на следующую страницу
            else:
                break
       
        except Exception as e:
            print(f"Error: {e}")
            break
    return count


print(get_users(1))



