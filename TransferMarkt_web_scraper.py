# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 15:41:34 2021

@author: amill
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time as time 
#url = 'https://www.transfermarkt.co.uk/west-ham-united/kader/verein/379/plus/0/galerie/0?saison_id=2020'

start = time.time()

name_list = []
current_club_list = []
value_list = []

clubs_url_list = list(range(1, 1001))

for club_url in clubs_url_list:
    url = 'https://www.transfermarkt.co.uk/manchester-city/kader/verein/' + str(club_url) + '/plus/0/galerie/0?saison_id=2020'
    while url == 'https://www.transfermarkt.co.uk/manchester-city/kader/verein/' + str(club_url) + '/plus/0/galerie/0?saison_id=2020':
        try:
            response = requests.get(url, headers={'User-Agent': 'Custom5'})
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
    
    #response = requests.get(url, headers={'User-Agent': 'Custom5'})
    #print(response.status_code)
    financial_data = response.text
    soup = BeautifulSoup(financial_data, 'html.parser')
    
    grouped_data_odd = soup.find_all('tr', {'class': 'odd'})
    grouped_data_even = soup.find_all('tr', {'class': 'even'})
    
    for result in grouped_data_odd:
        name = result.find('a', {'class': 'spielprofil_tooltip'}).text
        name_list.append(name)        
        if result.find('a', {'class': 'vereinprofil_tooltip'}) is None:
            current_club = 'Currently No Club/Unknown'
        else: 
            current_club = result.find('a', {'class': 'vereinprofil_tooltip'}).img.get('alt')
        current_club_list.append(current_club)
        if result.find('td', {'class': 'rechts hauptlink'}) is None:
            price = 'Unknown'
        else: 
            price = result.find('td', {'class': 'rechts hauptlink'}).text
        value_list.append(price)
       
        
    for result in grouped_data_even:
        name = result.find('a', {'class': 'spielprofil_tooltip'}).text
        name_list.append(name)
        if result.find('a', {'class': 'vereinprofil_tooltip'}) is None:
            current_club = 'Currently No Club/Unknown'
        else: 
            current_club = result.find('a', {'class': 'vereinprofil_tooltip'}).img.get('alt')
        current_club_list.append(current_club)
        if result.find('td', {'class': 'rechts hauptlink'}) is None:
            price = 'Unknown'
        else: 
            price = result.find('td', {'class': 'rechts hauptlink'}).text
        value_list.append(price)

end = time.time()
print('This program took ' + str(end-start) + ' to run.')

#%%
#turning all the dtata into a dataframe for pandas 
price_df = pd.DataFrame({'Name': name_list,
                           'Current Club': current_club_list,
                           'Value': value_list,
                            })

#%%
#loading in the stats dataframe 
all_2020_2021_stats = pd.read_csv('all_2020_2021_stats.csv')
all_2020_2021_stats.replace([np.inf, -np.inf], 0, inplace=True)

#%%
#joining the 2 stats and price dataframes by name 
#this fuzzy matching solution was taken from an answer on https://stackoverflow.com/questions/13636848/is-it-possible-to-do-fuzzy-match-merge-with-python-pandas
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def fuzzy_merge(df_1, df_2, key1, key2, threshold=90, limit=2):
    """
    :param df_1: the left table to join
    :param df_2: the right table to join
    :param key1: key column of the left table
    :param key2: key column of the right table
    :param threshold: how close the matches should be to return a match, based on Levenshtein distance
    :param limit: the amount of matches that will get returned, these are sorted high to low
    :return: dataframe with boths keys and matches
    """
    s = df_2[key2].tolist()
    
    m = df_1[key1].apply(lambda x: process.extract(x, s, limit=limit))    
    df_1['matches'] = m
    
    m2 = df_1['matches'].apply(lambda x: ', '.join([i[0] for i in x if i[1] >= threshold]))
    df_1['matches'] = m2
    
    return df_1

stats_and_price_df = fuzzy_merge(all_2020_2021_stats, price_df, 'player', 'Name', threshold=80)