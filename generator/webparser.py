'''
Created on 16 août 2018

@author: juliette.bourquin
'''
import requests
import re
import os
import codecs
from bs4 import BeautifulSoup

visited = []
# future has to be instantiated with a token address so the while loop can start on something
future = []
forbidden = ['haru', 'natu', 'aki', 'huyu', 'tanka', 'utamakura', 'kojiki', 'kaihusou', 'manyohshyu', 
             'isestory', 'kokin', 'gosen', 'shyui', 'genji', 'gshyui', 'kinyo', 'sika', 'senzai', 'skokin', 
             'schoku', 'okunohosomichi', 'nozarasi', 'kasimamoude', 'index']                          

def extract_content(address):
    if address not in visited:
        r = requests.get(address)
        r.encoding = 'shift_jis'
        text = r.text
        soup = BeautifulSoup(text, 'lxml')
        # checking whether we are on the page of an author or on an index :
        if not 'index' in address :
            # extracting author's name from url provided
            auteur = re.sub('http\://www5c\.biglobe\.ne\.jp/\~n32e131/haiku/', '', address)
            auteur = re.sub('\.html', '', auteur)
            auteur = re.sub('([0-9])*', '', auteur)
            with open('../sourcetexts/'+auteur+'.txt', 'a+', encoding='utf-8') as r_file:
                for p in soup.find_all('p'):
                    haiku = ''.join(p.findAll(text=True))
                    r_file.write(haiku+'\n')
        # find reference to other parts of website
        for ref in soup.find_all('a'):
            # if they are not in the list of url visited 
            if 'href' in ref.attrs :
                root = 'http://www5c.biglobe.ne.jp/~n32e131/haiku/'
                url = ref['href']
                safety_check = re.match('(.)*?(haru|natu|aki|huyu|tanka|utamakura|kojiki|kaihusou|manyohshyu|\
                                        isestory|kokin|gosen|shyui|genji|gshyui|kinyo|sika|senzai|skokin|\
                                        schoku|okunohosomichi|nozarasi|kasimamoude)/([a-zA-Z0-9])*?\.htm(l)*', url)
                safety_check2 = re.match('https(.)*', url)
                if 'index' not in url and '..' not in url and safety_check is None and safety_check2 is None:
                    url = root + url   
                    if url not in visited and url not in future :        
                        # add them to the list of urls to visit (caution, check that only applies to authors name)            
                        future.append(url)
        # IMPORTANT : check whether address has same structure than url in website                
        visited.append(address)                     
        future.remove(address)
    
def iterate(root):
    future.append(root)
    while len(future) > 0 :
        extract_content(future[0])
        print(len(future))
        print(future)
        
if __name__ == '__main__':

    root = 'http://www5c.biglobe.ne.jp/~n32e131/haiku/index.html'
    iterate(root)