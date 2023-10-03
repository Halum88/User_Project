from fake_useragent import UserAgent
import random
import os
import psycopg2
from bs4 import BeautifulSoup
from requests import get
from threading import Timer


url = os.environ['URL_SCRAPP']
base_url = os.environ['BASE_URL']
db_name = os.environ['DB_NAME']
user_name = os.environ['USER_NAME']
user_pw = os.environ['USER_PW']
proxy_dict = []
region_dict = {}
ua = UserAgent()
headers = {'User-Agent': ua.random} #рандомный user-agent
dict_ok = []
max_id = 1
m_id = 1



###Рандомный прокси из БД###
def rand_proxi():     
    try:
        db = psycopg2.connect(
                    database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
                )   
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
        

###Получаем мксимальное значение id в БД###
def maxim_ip_id():
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
    except Exception as e: 
        print("ERROR in DB - maxim ip id: ", e) 
    finally:
        db.close()  


def maxim_ooo_id():
    try:
        db = psycopg2.connect(
                database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
            )   
        cursor = db.cursor() 
        cursor.execute('select max(id) from companies')
        
        global m_id
        m_id = cursor.fetchone()[0]
        if m_id is None:
            m_id = 0
    except Exception as e: 
        print("ERROR in DB - maxim ooo id: ", e) 
    finally:
        db.close()  


###Все регионы из БД###
def region_id():
    try:
        db = psycopg2.connect(
                database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
            )   
        cursor = db.cursor() 
        cursor.execute('''SELECT id, name FROM region''')
        records = cursor.fetchall()
        for i in records:
            region_dict[i[1]] = i[0]
        return region_dict
    except Exception as error:   
         print("ERROR in DB - region id: ", error) 
    finally:
        db.close() 


###Создаем сессию###
def session():
        prx = rand_proxi()
        proxi = random.choice(prx)
        return proxi


def scrapper():
    global max_id
    global m_id
    global region_dict
    scrapper.call_count += 1

    if scrapper.call_count > 3:
        print("Nope...")
        return
    
    
    db = psycopg2.connect(
                database = db_name, user = user_name, password = user_pw, host="127.0.0.1", port="5432"
            )   
    cursor = db.cursor() 


    proxi = session()
    proxis = {"http://": proxi, "https://": proxi}
    try:
        response = get(url, headers=headers, proxies=proxis, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        reg_list = soup.find_all('a', class_='contragent-link')
        for reg in reg_list:
            region = reg.text   #Регионы
            link = reg['href']   #Ссылки регионов

            ###Запись регионов в бд###
            if len(region_dict) == 0 or region not in region_dict:
                cursor.execute('''INSERT INTO region(id, name, link) VALUES(%s, %s,%s)
                               ON CONFLICT (link)
                               DO NOTHING
                               RETURNING id''',(None, region, link))
                id_db = cursor.fetchone()
                region_dict[region] = id_db[0]
            
            ###Получаем все ИП в каждом регионе и записываем в БД###
            
            url_reg = base_url+link
            response = get(url_reg, headers=headers, proxies=proxis, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            user_i = soup.find_all('div', class_='tr tbody-tr')
            try:
                for user in user_i:
                    name = user.find('div', class_='td').find('a').text              #Имя
                    
                    ### Скрап ИП
                    if name.startswith('ИП'):
                        l = user.find('div', class_='td').find('a', href=True)['href']   
                        link = base_url+l                                                #Ссылка
                        status = user.find('div', class_='td__text').text                #Статус
                        city = user.find_all('div', class_='td__text')[1].text           #Город
                        address = user.find_all('div', class_='td__text')[2].text        #Адрес
                        ogrn = user.find_all('div', class_='td__text')[3].text           #ОГРН
                        inn = user.find_all('div', class_='td__text')[4].text            #ИНН
                        activity = user.find_all('div', class_='td__text')[5].text       #ОКВЭД
                        date_registr = user.find_all('div', class_='td__text')[6].text   #Дата регистрации
                
                        if status == 'Действует':     
                            max_id += 1
                            cursor.execute(('''INSERT INTO users(id,name,status,city,address,ogrn,inn,activity,date,region_id) 
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                            ON CONFLICT (inn)
                                            DO UPDATE
                                            SET name=%s, status=%s,city=%s,address=%s, 
                                            ogrn=%s,activity=%s,date=%s,region_id=%s
                                            '''),[max_id,name,status,city,address,ogrn,inn,activity,date_registr,int(region_dict[region]),name,status,city,address,ogrn,activity,date_registr,int(region_dict[region])])
                    
                    ### Скрап ООО
                    elif not name.startswith('ИП'):
                        l = user.find('div', class_='td').find('a', href=True)['href']   
                        link = base_url+l                                                #Ссылка
                        status = user.find('div', class_='td__text').text                #Статус
                        city = user.find_all('div', class_='td__text')[1].text           #Город
                        address = user.find_all('div', class_='td__text')[2].text        #Адрес
                        manager = user.find_all('div', class_='td__text')[3].text        #Руководитель
                        ogrn = user.find_all('div', class_='td__text')[4].text           #ОГРН
                        inn = user.find_all('div', class_='td__text')[5].text            #ИНН
                        capital = user.find_all('div', class_='td__text')[6].text        #Уставной капитал
                        activity = user.find_all('div', class_='td__text')[7].text       #ОКВЭД
                        date_registr = user.find_all('div', class_='td__text')[8].text   #Дата регистрации
                        
                        if status == 'Действует':     
                            m_id += 1
                            cursor.execute(('''INSERT INTO companies(id,name,status,city,address,region_id,manager,ogrn,inn,capital,activity,date) 
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                            ON CONFLICT (inn)
                                            DO UPDATE
                                            SET name=%s, status=%s,city=%s,address=%s,region_id=%s, manager=%s,
                                            ogrn=%s,capital=%s,activity=%s,date=%s
                                            '''),[m_id,name,status,city,address,int(region_dict[region]),manager,ogrn,inn,capital,activity,date_registr,name,status,city,address,int(region_dict[region]), manager,ogrn, capital,activity,date_registr])
                    
                    
                    
                    
                    else:
                        continue
        
            except Exception as e:
                print('ERROR ---',e)
            
    except Exception as error:
        print('Error:',proxi,'---', error)
        Timer(4, scrapper).start()

    db.commit()
    db.close() 
scrapper.call_count = 0


###___main___###
maxim_ip_id()
maxim_ooo_id()
region_id()
scrapper()