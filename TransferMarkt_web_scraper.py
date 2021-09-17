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
    #following part was taken from https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests 
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
import numpy as np 
all_2020_2021_stats = pd.read_csv('all_2020_2021_stats.csv')
all_2020_2021_stats.replace([np.inf, -np.inf], 0, inplace=True)

#%%
# creating a per 90 dataframe 
#also this is cleaning the data a lot 
per_90_stats = all_2020_2021_stats.drop(columns = ['shots_total_per90', 'shots_on_target_per90', 'gca_per90', 'sca_per90', 'Interceptions/90', 'Tackles won/90', 'Tackles/90'])
per_90_stats = per_90_stats.drop(['Unnamed: 0', 'Unnamed: 0.1'], axis = 1)


#%%
#creating a list of the columns 
per_90_columns = []
for col in per_90_stats:
    per_90_columns.append(col)
#print(per_90_columns)

#creating a new data frame 
per_90_2020_2021_stats = pd.DataFrame(columns = per_90_columns)

#specifying which columns need to per made into per 90 
rows_to_change = ['passes_completed', 'passes', 'passes_total_distance', 'passes_progressive_distance', 'passes_completed_short', 'passes_short', 'passes_completed_medium', 'passes_medium', 'passes_completed_long', 'passes_long', 'assists', 'xa', 'xa_net', 'assisted_shots', 'passes_into_final_third', 'passes_into_penalty_area', 'crosses_into_penalty_area', 'progressive_passes', 'goals', 'npxg', 'npxg_net', 'pens_att', 'pens_made', 'shots_free_kicks', 'shots_on_target', 'shots_total', 'xg', 'xg_net', 'gca', 'gca_defense', 'gca_dribbles', 'gca_fouled', 'gca_passes_dead', 'gca_passes_live', 'gca_shots', 'sca', 'sca_defense', 'sca_dribbles', 'sca_fouled', 'sca_passes_dead', 'sca_passes_live', 'sca_shots', 'blocked_passes', 'blocked_shots', 'blocked_shots_saves', 'clearances', 'dribble_tackles',  'dribbled_past', 'dribbles_vs', 'errors', 'interceptions', 'pressure_regains', 'pressures', 'pressures_att_3rd', 'pressures_def_3rd', 'pressures_mid_3rd', 'tackles', 'tackles_att_3rd', 'tackles_def_3rd', 'tackles_interceptions', 'tackles_mid_3rd', 'tackles_won']

#iterating through the rows and then appending these new rows to the new dataframe we made 
for index, row in per_90_stats.iterrows():
    #print(row.loc['passes_completed':'tackles_won'])
    #print(row['minutes_90s'])
    if row['minutes_90s'] == 0:
        row.loc['passes_completed':'tackles_won'] = 0 
    else: row.loc[rows_to_change] = row.loc[rows_to_change]/row['minutes_90s']
    per_90_2020_2021_stats = per_90_2020_2021_stats.append(row)

#Should I adding the absolute stats to the end of the new dataframe where I feel it is necessary? Like total goals and assists etc. 


#%%
#merging the price and stats data frames together where the names exactly match 
merged = pd.merge(per_90_2020_2021_stats, right=price_df, left_on='player', right_on='Name')
#problem with the above is we miss out quite a lot of players (reduces from 2822 to 2145) 

#%%
#creating a dataframe with players who have played over 5 games 
over_5_games = per_90_2020_2021_stats.loc[(per_90_2020_2021_stats['minutes_90s'] >= 5)]

#testing it on an ML 
# =============================================================================
# from sklearn.model_selection import train_test_split
# from sklearn import linear_model 
# import matplotlib.pyplot as plt 
# 
# features = ['shots_on_target', 'average_shot_distance']
# target = 'xg'
# 
# y = over_5_games[target].values
# X = over_5_games[features].values
# 
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
# 
# lm = linear_model.LinearRegression()
# model = lm.fit(X_train, y_train)
# predictions = lm.predict(X_test)
# 
# plt.scatter(y_test, predictions)
# plt.xlabel('Actual Values')
# plt.ylabel('Predictions')
# 
# print('Score:', model.score(X_test, y_test))
# =============================================================================

#%%

#test stuff for the function below 
# =============================================================================
# player_name = 'Declan Rice'
# player_row_data = over_5_games.loc[over_5_games['player'] == player_name]
# print(player_row_data)
# attribute = 'minutes_90s'
# print(player_row_data[attribute].values)
# =============================================================================
#this is what I am trying to do in the for loop of the function 
# =============================================================================
# attribute = 'minutes_90s'
# new_df = over_5_games[over_5_games[attribute].between(25, 30)]
# attribute = 'interceptions'
# new_df = new_df[new_df[attribute].between(0.5, 2)]
# =============================================================================

#function to sort through a dataframe to try and find similar rows
def find_similar(player_name, attribute_1, stats_csv, *args):
    attributes = [attribute_1]
    
    #setting threshold to 0.2 (20%)
    threshold=0.2
    
    #the **kwargs function allows us to add extra attributes if needed
    for arg in args:
        attributes.append(arg)
    
    #getting the info of the player from the name given 
    player_row_data = over_5_games.loc[over_5_games['player'] == player_name]
    
    #getting the between values to find similar rows and then applying it for each attribute given. 
    for attribute in attributes:
        #print(attributes)
        value = player_row_data[attribute].values[0]
        #print(value)
        upper_limit = value*(1+threshold)
        lower_limit = value*(1-threshold)
        stats_csv = stats_csv[stats_csv[attribute].between(lower_limit, upper_limit)]
        #print(stats_csv)
     
    #this is just so I dont get confused on what is being outputted
    output_csv = stats_csv 
    return output_csv 

#gonna be honest, canny believe this worked 
similar_to_DR = find_similar('Declan Rice', 'pressures', over_5_games, 'passes', 'interceptions', 'tackles')        

#%%
#THIS NEEDS FIXING 
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

stats_and_price_df = fuzzy_merge(all_2020_2021_stats, price_df, 'player', 'Name', threshold=90)
