import os
from bs4 import BeautifulSoup
from requests import get



base_url = 'https://free-proxy-list.net/'
count = 0
proxy_dict = []

#def init_db():


def scrapping():
    response = get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxy_list = soup.find('table', class_ = 'table table-striped table-bordered').find_all('tr')[1:]
    global proxy_dict
    
    try:
        for port in proxy_list:
            tds = port.find_all('td')
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxy_dict.append(host)
        return proxy_dict
    
    except Exception as error:
        print('Error', error)   

    





#___main___#

scrapping()

