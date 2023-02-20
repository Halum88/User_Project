import os
from bs4 import BeautifulSoup
from requests import get



base_url = 'https://free-proxy-list.net/'
count = 0
dict = []
#def init_db():

def scrapping():
    response = get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxy_list = soup.find('div', class_ = 'table-responsive fpl-list')
    global count
    global dict
    
    
    
    try:
        for all_proxy in proxy_list:
            ip = all_proxy.find_all('tr')
            for j in ip:
                ip_2 = j.find('td')
                dict.append(ip_2)
        print(dict)
    

  #all_task.find('div', {'class':'divider'}).find('span', {'class':'comments-count'})['title']          
            
    
        
    except Exception as error:
        return error

#___main___#

scrapping()

