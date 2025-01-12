import os
import psycopg2
from requests import get
from dotenv import load_dotenv

load_dotenv()


db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']
check_url = os.environ['CHECK_URL']
proxi_err = []
count=0

def check_prx():
    global count
    try:
        db = psycopg2.connect(
            database = db_name, 
            user = user_name, 
            password = user_pw, 
            host=db_host, 
            port=db_port
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
                con = get(check_url, proxies=proxies, timeout=0.9).text.strip()
                if con == (str(px).split(':')[0]):
                    print('Proxy is working: ', px)
                    
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
