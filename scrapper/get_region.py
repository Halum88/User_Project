from fake_useragent import UserAgent
import os
import psycopg2
from bs4 import BeautifulSoup
from requests import get
from threading import Timer
from dotenv import load_dotenv
from psycopg2.extras import DictCursor



load_dotenv()


url = os.environ['URL_SCRAPP']
base_url = os.environ['BASE_URL']
db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']



def connect_db():
    db = psycopg2.connect(
        database = db_name,
        user = user_name,
        password = user_pw,
        host=db_host,
        port=db_port
        )
    return db


def rand_proxi():     
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute('''SELECT host FROM proxy ORDER BY random() LIMIT 1''')
        host = cursor.fetchone()
        if host is not None:
            return host[0]
        else:
            return None
    except Exception as e:
        print('ERROR in DB - random proxies: ', e)
    finally:
        db.close()


# получение регионов
def get_region():
    region_set = set() 

    try:
        proxis = {"http://": rand_proxi(), "https://": rand_proxi()}
        headers = {'User-Agent': UserAgent().random}

        response = get(url, headers=headers, proxies=proxis, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        reg_list = soup.find_all('a', class_='contragent-link')

        regions = []
        for reg in reg_list:
            region = reg.text.strip()
            link_reg = reg.get('href')

            if link_reg and region not in region_set:
                regions.append((region, link_reg))
                region_set.add(region) 

        regions.sort(key=lambda x: x[0]) 


        with connect_db() as db:
            with db.cursor(cursor_factory=DictCursor) as cursor:
                for region, link_reg in regions:
                    cursor.execute('''INSERT INTO region(name, link)
                        VALUES(%s, %s)
                        ON CONFLICT (link)
                        DO NOTHING
                        RETURNING id''', (region, link_reg))
                    
                    db.commit()


    except Exception as e:
        print('ERROR in get_region: ', e)




# получение региона из БД  
def get_region_in_db(num=None):
    region_dict = []
    db = connect_db()
    cursor = db.cursor() 

    try:
        cursor.execute('select * from region')
        records = cursor.fetchall()
        if records is None:
            get_region()
            cursor.execute('select * from region')
            records = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        if db:
            db.close()
    
    if records is not None:
        for i in records:
            region_dict.append(f"{i[1]}")  
        if num is not None:
            if num < len(region_dict):
                return region_dict[num]
            else:
                return 'No region with this number'
        else:
            return region_dict
