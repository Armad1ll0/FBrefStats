# -*- coding: utf-8 -*-
"""
Created on Fri Sep  3 19:09:35 2021

@author: amill
"""

#bulk of code was taken from this link - https://stackoverflow.com/questions/66517625/attributeerror-nonetype-object-has-no-attribute-text-beautifulshop

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import sys, getopt
import csv

def get_tables(url):
    res = requests.get(url)
    ## The next two lines get around the issue with comments breaking the parsing.
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("",res.text),'lxml')
    all_tables = soup.findAll("tbody")
    team_table = all_tables[0]
    player_table = all_tables[2]
    return player_table, team_table

def get_frame(features, player_table):
    pre_df_player = dict()
    features_wanted_player = features
    rows_player = player_table.find_all('tr')
    for row in rows_player:
        #print(row)
        if(row.find('th',{"scope":"row"}) != None):
            #print(row)
            for f in features_wanted_player:
                #print(f)
                cell = row.find("td",{"data-stat": f})
                #print(f)
                #print(cell)
                a = cell.text.strip().encode()
                text=a.decode("utf-8")
                #print(text)
                if(text == ''):
                    text = '0'
                if((f!='player')&(f!='nationality')&(f!='position')&(f!='squad')&(f!='age')&(f!='birth_year')):
                    text = float(text.replace(',',''))
                if f in pre_df_player:
                    pre_df_player[f].append(text)
                else:
                    pre_df_player[f] = [text]
    df_player = pd.DataFrame.from_dict(pre_df_player)
    return df_player

stats = ["player","nationality","position","squad","age",'birth_year', "minutes_90s","tackles","tackles_won","tackles_def_3rd","tackles_mid_3rd","tackles_att_3rd", "dribble_tackles", "dribbles_vs","dribble_tackles_pct","dribbled_past","pressures","pressure_regains","pressure_regain_pct","pressures_def_3rd","pressures_mid_3rd","pressures_att_3rd","blocked_shots","blocked_shots_saves", "blocked_passes", "interceptions", "tackles_interceptions", "clearances", "errors"]

def frame_for_category(category,top,end,features):
    url = (top + category + end)
    player_table, team_table = get_tables(url)
    df_player = get_frame(features, player_table)
    return df_player

top='https://fbref.com/en/comps/9/'
end='Premier-League-Stats'
defensive_stats_eng_2020_2021 = frame_for_category('10728/defense/2020-2021-',top,end,stats)

#web = 'https://fbref.com/en/comps/13/10732/2020-2021-Ligue-1-Stats'
top='https://fbref.com/en/comps/13/'
end='Ligue-1-Stats'
defensive_stats_fr_2020_2021 = frame_for_category('10732/defense/2020-2021-', top,end,stats)

#web = 'https://fbref.com/en/comps/20/10737/defense/2020-2021-Bundesliga-Stats'
top='https://fbref.com/en/comps/20/'
end='Bundesliga-Stats'
defensive_stats_ger_2020_2021 = frame_for_category('10737/defense/2020-2021-', top,end,stats)

#web = 'https://fbref.com/en/comps/11/10730/defense/2020-2021-Serie-A-Stats'
top='https://fbref.com/en/comps/11/'
end='Serie-A-Stats'
defensive_stats_ita_2020_2021 = frame_for_category('10730/defense/2020-2021-', top,end,stats)

#web = 'https://fbref.com/en/comps/12/10731/defense/2020-2021-La-Liga-Stats'
top='https://fbref.com/en/comps/12/'
end='La-Liga-Stats'
defensive_stats_spa_2020_2021 = frame_for_category('10731/defense/2020-2021-', top,end,stats)

#merging the top 5 leagues data 
defensive_stats_big5_2020_2021 = defensive_stats_eng_2020_2021.append([defensive_stats_fr_2020_2021, defensive_stats_ger_2020_2021, defensive_stats_ita_2020_2021, defensive_stats_spa_2020_2021])

#%%

#making some adjustments to the data where I think it wuld be useful 
defensive_stats_big5_2020_2021.insert(9, 'Tackles won/attempted', defensive_stats_big5_2020_2021['tackles_won']/defensive_stats_big5_2020_2021['tackles'])
defensive_stats_big5_2020_2021.insert(8, 'Tackles/90', defensive_stats_big5_2020_2021['tackles']/defensive_stats_big5_2020_2021['minutes_90s'])
defensive_stats_big5_2020_2021.insert(10, 'Tackles won/90', defensive_stats_big5_2020_2021['tackles_won']/defensive_stats_big5_2020_2021['minutes_90s'])
#print(len(defensive_stats.columns))
defensive_stats_big5_2020_2021.insert(29, 'Interceptions/90', defensive_stats_big5_2020_2021['interceptions']/defensive_stats_big5_2020_2021['minutes_90s'])


#%%
#example of how to scan through the data for specific attributes 
best_tackler = defensive_stats_big5_2020_2021.loc[(defensive_stats_big5_2020_2021['minutes_90s'] >= 20) & (defensive_stats_big5_2020_2021['Tackles won/90'] >= 1.5) & (defensive_stats_big5_2020_2021['Interceptions/90'] >= 1.5)]

#%%
#trying to make a radar graph when someones name is entered 

import matplotlib.pyplot as plt
from scipy import stats

def player_def_radar(player_name):
    #finding the rows we need from the name 
    row = defensive_stats_big5_2020_2021.loc[defensive_stats_big5_2020_2021['player'] == player_name]
    #creating a new dataframe that we can create a radar graph from 
    columns = ['Defensive Stats', 'Percentile']
    df = pd.DataFrame(columns=columns)
    #slicing the dataframe as we canny compare names really 
    comparison_vals = defensive_stats_big5_2020_2021.loc[:, 'minutes_90s':'errors']
    for column in comparison_vals:
        #print(row[column])
        #print(comparison_vals[column])
        percentile = stats.percentileofscore(comparison_vals[column], row[column].iloc[0], kind='mean')
        #creating a new row from the percentile data gained above 
        new_row = {'Defensive Stats':column, 'Percentile': percentile}
        #appending new data to the DF
        df = df.append(new_row, ignore_index = True)
    
    #this was taken from https://stackoverflow.com/questions/60231146/how-can-i-turn-my-dataframe-into-a-radar-chart-using-python
    fig = plt.figure(figsize=(14, 8), dpi=200)
    ax = fig.add_subplot(111, projection="polar")
    
    # theta has different angles, and the first one repeated
    theta = np.arange(len(df) + 1) / float(len(df)) * 2 * np.pi
    # values has the values from 'Col B', with the first element repeated
    values = df['Percentile'].values
    values = np.append(values, values[0])
    
    # draw the polygon and the mark the points for each angle/value combination
    l1, = ax.plot(theta, values, color="C2", marker="o", label="Name of Col B")
    plt.xticks(theta[:-1], df['Defensive Stats'], color='grey', size=12)
    ax.tick_params(pad=10) # to increase the distance of the labels to the plot
    # fill the area of the polygon with green and some transparency
    ax.fill(theta, values, 'green', alpha=0.1)
    
    # plt.legend() # shows the legend, using the label of the line plot (useful when there is more than 1 polygon)
    plt.title("Defensive Stats of " + str(player_name) +'\n' + 'Given in Percentiles.')
    
    return plt.show()
    
player_def_radar('Michail Antonio')