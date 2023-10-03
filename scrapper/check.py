import os
import requests
import random
import psycopg2
import time
from requests import get
from bs4 import BeautifulSoup


base_url = os.environ['PROXY_URL']
db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
proxi_err = []
count=0

def check_prx():
    global count
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
    
    cursor.execute('''select host from proxy''')
    proxy = cursor.fetchall()
    for i in proxy:
        for px in i:
            proxies = {"http": px, "https": px}
            try:
                con = get('http://icanhazip.com', proxies=proxies, timeout=0.9).text.strip()
                if con == (str(px).split(':')[0]):
                    pass
                else:
                    proxi_err.append(px)
            except Exception as error:
                continue
                
    for k in proxi_err:
        try:
            cursor.execute('''DELETE FROM proxy WHERE host = %s''', [k])
            count += 1            
        except Exception as err:
            raise Exception('Not delete:', err)        
    
    print('Delete proxis: ', count)
    
    db.commit()
    db.close()    
   

###___main___###
check_prx()
