#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 20:38:42 2021

@author: anonimo
"""

import pandas as pd
import numpy as np
import re

from bs4 import BeautifulSoup
import requests

import os

"""
    Functions to use
"""

def initialize(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
    page = requests.get(url,
                    headers=headers
                    )
    soup = BeautifulSoup(page.content,
                     'html.parser'
                     )
    return soup


def extract(obj):
    data = []
    for i in range(len(obj)):
        d = obj[i].get_text()
        data.append(d)
    return data

def extract_links(obj):
    data = []
    link_first = 'https://www.transfermarkt.com'
    for i in range(len(obj)):
        d = obj[i].get('href')
        data.append(link_first + d)
    return data

def extract_data_tab(obj):
    data_tab = []
    for i in range(len(obj)):
        exclude = re.compile('no-border-rechts')
        if exclude.search(str(obj[i])):
            continue
        else:
            d = obj[i].get_text()
            data_tab.append(d)
    return data_tab


"""
    End Functions
"""

"""
    Get the 20 pages of Most Valuable Players and names/links of the players
"""

url2 = 'https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop?ajax=yw1&altersklasse=alle&ausrichtung=alle&jahrgang=0&kontinent_id=0&land_id=0&spielerposition_id=alle&page='
players_urls = []
players_names = []
players_link = []

for i in range(1,21):
    new = url2 + str(i)
    players_urls.append(new)


print('Getting players names and links...')
count = 0
for url in players_urls:
    soup_loop = initialize(url)
    names = soup_loop.find('div', class_='responsive-table')\
                    .find_all(class_='spielprofil_tooltip')
    players_names_loop = extract(names)
    players_link_loop = extract_links(names)
    players_names += players_names_loop
    players_link += players_link_loop
    work = round((count/len(players_urls))*100, 0)
    print('{}%'.format(work))
    count += 1


for i in range(len(players_link)):
    players_link[i] = players_link[i].replace('profil', 'transfers')

players_names_links = dict(zip(players_names, players_link))

print('Finish getting 500 players names and links')

"""
    Get the players data
"""

soup = initialize(players_link[0])
columns_names = extract(soup.find_all('thead')[0].find_all('th'))
# row_qty = len(extract(soup.find_all('tbody')[0].find_all('tr')))
col_qty = len(columns_names)

players_transfers = {}


print('Gathering data...')
count = 0
for name, link in players_names_links.items():
    soup = initialize(link)    
    #tables = soup.find_all('tbody')
    tables = soup.find_all('tr', 'zeile-transfer')
    data = []
    for i in range(len(tables)):
        data += extract_data_tab(tables[i].find_all('td'))
    players_transfers[name] = data
    work = round((count/len(players_names_links))*100, 2)
    print('{}% - Working on {}...'.format(work, name))
    count += 1


print('Finish gathering data')



"""
    Funciona perfectamente pero necesito saber como dejar todo en una tabla
    plana porque está en un diccionario:
        
    'Kylian Mbappé': ['18/19', 'Jul 1, 2018', '€120.00m', '€145.00m', '\n\n',
                      '17/18', 'Jun 30, 2018', '€120.00m', 'End of loan', '\n\n',
                      '17/18', 'Aug 31, 2017', '€35.00m', 'loan transfer', '\n\n',
                      '15/16', 'Dec 1, 2015', '-', '-', '\n\n',
                      '15/16', 'Jul 1, 2015', '-', '-', '\n\n',
                      '13/14', 'Jul 1, 2013', '-', 'free transfer', '\n\n'],
    
    'Harry Kane': ['12/13', 'May 14, 2013', '€500Th.', 'End of loan', '\n\n',
                   '12/13', 'Feb 21, 2013', '€500Th.', 'loan transfer', '\n\n',
                   '12/13', 'Feb 1, 2013', '€500Th.', 'End of loan', '\n\n',
                   '12/13', 'Aug 31, 2012', '-', 'loan transfer', '\n\n',
                   '11/12', 'May 31, 2012', '-', 'End of loan', '\n\n',
                   '11/12', 'Jan 1, 2012', '-', 'loan transfer', '\n\n',
                   '10/11', 'May 31, 2011', '-', 'End of loan', '\n\n',
                   '10/11', 'Jan 7, 2011', '-', 'loan transfer', '\n\n',
                   '10/11', 'Jan 1, 2011', '-', '-', '\n\n',
                   '09/10', 'Jul 1, 2009', '-', '-', '\n\n']
    ...
    
"""


players_data = pd.DataFrame()

for key, value in players_transfers.items():
    print('Player {}...'.format(key))
    to_df = np.reshape(value, (int(len(value)/col_qty), col_qty))
    to_df = pd.DataFrame(to_df)
    to_df['player'] = key
    players_data = players_data.append(to_df)
    

players_data.columns = columns_names + ['player']
players_data.drop(columns=players_data.columns[6], inplace=True)

"""
    Save the data to a CSV or SQL
"""

players_data.to_csv('players_transfers_data.csv',
                    index=False,
                    encoding='utf-8'
                    )
    
