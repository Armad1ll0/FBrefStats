# -*- coding: utf-8 -*-
"""
Created on Fri Sep  3 17:44:16 2021

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
        if(row.find('th',{"scope":"row"}) != None):
            #print(row)
            for f in features_wanted_player:
                #print(f)
                cell = row.find("td",{"data-stat": f})
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

stats = ["player","nationality","position","squad","age",'birth_year', "minutes_90s","goals","shots_total","shots_on_target","shots_on_target_pct","shots_total_per90", "shots_on_target_per90", "goals_per_shot","goals_per_shot_on_target","average_shot_distance","shots_free_kicks","pens_made","pens_att","xg","npxg","npxg_per_shot","xg_net","npxg_net"]

def frame_for_category(category,top,end,features):
    url = (top + category + end)
    player_table, team_table = get_tables(url)
    df_player = get_frame(features, player_table)
    return df_player

top='https://fbref.com/en/comps/9/10728/'
end='Premier-League-Stats'
shooting_stats_eng_2020_2021 = frame_for_category('shooting/2020-2021-',top,end,stats)

#web = 'https://fbref.com/en/comps/13/10732/shooting/2020-2021-Ligue-1-Stats'
top='https://fbref.com/en/comps/13/'
end='Ligue-1-Stats'
shooting_stats_fr_2020_2021 = frame_for_category('10732/shooting/2020-2021-', top,end,stats)

#web = 'https://fbref.com/en/comps/20/10737/shooting/2020-2021-Bundesliga-Stats'
top='https://fbref.com/en/comps/20/'
end='Bundesliga-Stats'
shooting_stats_ger_2020_2021 = frame_for_category('10737/shooting/2020-2021-', top,end,stats)

#web = 'https://fbref.com/en/comps/11/10730/shooting/2020-2021-Serie-A-Stats'
top='https://fbref.com/en/comps/11/'
end='Serie-A-Stats'
shooting_stats_ita_2020_2021 = frame_for_category('10730/shooting/2020-2021-', top,end,stats)

#web = 'https://fbref.com/en/comps/12/10731/defense/2020-2021-La-Liga-Stats'
top='https://fbref.com/en/comps/12/'
end='La-Liga-Stats'
shooting_stats_spa_2020_2021 = frame_for_category('10731/shooting/2020-2021-', top,end,stats)

#merging the top 5 leagues data 
shooting_stats_big5_2020_2021 = shooting_stats_eng_2020_2021.append([shooting_stats_fr_2020_2021, shooting_stats_ger_2020_2021, shooting_stats_ita_2020_2021, shooting_stats_spa_2020_2021])

#%%
shooting_stats_big5_2020_2021.to_csv('FB_ref_shooting_stats_2020_2021.csv', encoding = 'utf-8')
#trying to make a radar graph when someones name is entered
#add in per 90 stats as this makes more sense. 
#implement somethign so you can alter the data frame with number of minutes played. Might make the stats make more sense.  

import matplotlib.pyplot as plt
from scipy import stats

def player_shoot_radar(player_name, shooting_stats_big5_2020_2021):
    #finding the rows we need from the name 
    #need to somehow get rid of the accents in players names, can be done at a later time. 
    row = shooting_stats_big5_2020_2021.loc[shooting_stats_big5_2020_2021['player'] == player_name]
    #creating a new dataframe that we can create a radar graph from 
    columns = ['Shooting Stats', 'Numbers', 'Percentile']
    df = pd.DataFrame(columns=columns)
    #slicing the dataframe as we canny compare names really 
    comparison_vals = shooting_stats_big5_2020_2021.loc[:, 'minutes_90s':'npxg_net']
    for column in comparison_vals:
        #print(row[column])
        #print(comparison_vals[column])
        percentile = stats.percentileofscore(comparison_vals[column], row[column].iloc[0], kind='rank')
        #creating a new row from the percentile data gained above 
        new_row = {'Shooting Stats':column, 'Percentile': percentile, 'Numbers': row[column].iloc[0]}
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
    plt.xticks(theta[:-1], df['Shooting Stats'], color='grey', size=12)
    ax.tick_params(pad=10) # to increase the distance of the labels to the plot
    # fill the area of the polygon with green and some transparency
    ax.fill(theta, values, 'green', alpha=0.1)
    
    # plt.legend() # shows the legend, using the label of the line plot (useful when there is more than 1 polygon)
    plt.title("Shooting Stats of " + str(player_name) +'\n' + 'Given in Percentiles.')
    print(df)
    return plt.show(), df

#stats for some players may be expontential as this includes players who have only played a few minutes as well. 
player_shoot_radar('Lionel Messi', shooting_stats_big5_2020_2021)

