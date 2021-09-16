# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 17:50:31 2021

@author: amill
"""

#TO DO LIST: 
#This will be the basic outlay of how to get stats from a player from the other FB ref files 
#this stuff is all functional but I need to make a front end out of it and make it more pretty 
#also need to add the rest of the potential stats of players but thats just time consuming not hard 
#the functions might have to be altered slightly in order to make it more pretty but it works for now 
#also need to do it for previous years and update the current year week on week 

import pandas as pd 
#need to change the file names so they can be imported 
from FB_Ref_Player_Passing_Stats import player_passing_radar
from FB_Ref_Player_Defensive_Stats import player_def_radar
from FB_Ref_Player_Shooting_Stats import player_shoot_radar
from FB_Ref_Player_Shot_Creation_Stats import player_shot_creation_radar
import numpy as np 

passing_stats_2020_2021 = pd.read_csv('FB_ref_passing_stats_2020_2021.csv')
shooting_stats_2020_2021 = pd.read_csv('FB_ref_shooting_stats_2020_2021.csv')
shot_creation_stats_2020_2021 = pd.read_csv('FB_ref_shot_creation_stats_2020_2021.csv')
defensive_stats_2020_2021 = pd.read_csv('FB_ref_defensive_stats_2020_2021.csv')

#%%
#merging all dataframes 
cols = shooting_stats_2020_2021.columns.difference(passing_stats_2020_2021.columns)
shoot_pass = passing_stats_2020_2021.join(shooting_stats_2020_2021[cols])
cols = shot_creation_stats_2020_2021.columns.difference(shoot_pass.columns)
shoot_pass_create = shoot_pass.join(shot_creation_stats_2020_2021[cols])
cols = defensive_stats_2020_2021.columns.difference(shoot_pass_create.columns)
shoot_pass_create_defend = shoot_pass_create.join(defensive_stats_2020_2021[cols])
all_2020_2021_stats = shoot_pass_create_defend
all_2020_2021_stats.to_csv('all_2020_2021_stats.csv', encoding = 'utf-8')

#%%
#example function of returning the stats of a player for a specific type of data 
player_shoot_radar('Harry Kane', shooting_stats_2020_2021)


#%%
#standard function that loads of all the stats graphs when you enter a players name. 
def player_radar_graphs(player_name, passing_csv, shooting_csv, shot_creation_csv, defensive_csv):
    return player_passing_radar(player_name, passing_csv), player_shoot_radar(player_name, shooting_csv), player_shot_creation_radar(player_name, shot_creation_csv), player_def_radar(player_name, defensive_csv)

player_radar_graphs('Dimitri Payet', passing_stats_2020_2021, shooting_stats_2020_2021, shot_creation_stats_2020_2021, defensive_stats_2020_2021)

#%%

#this is an example function of how to create a new dataframe from conditions that you want 
best_tackler = defensive_stats_2020_2021.loc[(defensive_stats_2020_2021['minutes_90s'] >= 20) & (defensive_stats_2020_2021['Tackles won/90'] >= 2.0) & (defensive_stats_2020_2021['Interceptions/90'] >= 1.5)]
best_tackler.to_csv('best_tackler.csv')

#%%
#this gives an average of the dataframe and a comparison of a player chosne in certain areas to the average 
#first we create a dataframe where only players who have over a certain amount of minutes played count 
over_5_games_def = defensive_stats_2020_2021.loc[(defensive_stats_2020_2021['minutes_90s'] >= 10)]
over_5_games_def.replace([np.inf, -np.inf], 0, inplace=True)
average_def = over_5_games_def.mean()
#average_def = average_def.loc[:, 'minutes_90s':'errors']
#choosing the player we want to compare with the average 
df_player_def = player_def_radar('Declan Rice', defensive_stats_2020_2021)[1]
df_player_def = df_player_def.loc[:, 'minutes_90s':'errors']
L = [average_def, df_player_def]
player_comparison_avg = pd.concat(L, axis = 1)


#%%
#player comparison graphs 
#need to figure out how to delay the output of these so they come out at the same time. 

def comparison_csv(player_name_1, player_name_2, keyword):
    if keyword == 'passing':
        img_A, df_1 = player_passing_radar(player_name_1, passing_stats_2020_2021)
        img_B, df_2 = player_passing_radar(player_name_2, passing_stats_2020_2021)
        
    elif keyword == 'shooting':
        img_A, df_1 = player_shoot_radar(player_name_1, shooting_stats_2020_2021)
        img_B, df_2 = player_shoot_radar(player_name_2, shooting_stats_2020_2021)
        
    elif keyword == 'shot creation':
        img_A, df_1 = player_shot_creation_radar(player_name_1, shot_creation_stats_2020_2021)
        img_B, df_2 = player_shot_creation_radar(player_name_2, shot_creation_stats_2020_2021)
        
    elif keyword == 'defensive':
        img_A, df_1 = player_def_radar(player_name_1, defensive_stats_2020_2021)
        img_B, df_2 = player_def_radar(player_name_2, defensive_stats_2020_2021)
    
    #canny use this code in spyder but moght be useful later on if I move it over to a notebook 
    # df1_styler = df_1.style.set_table_attributes("style='display:inline'").set_caption(str(player_name_1))
    # df2_styler = df_2.style.set_table_attributes("style='display:inline'").set_caption(str(player_name_1))
    # display_html(df1_styler._repr_html_()+df2_styler._repr_html_(), raw=True)
    
    return df_1, df_2
    
comparison_csv('Dimitri Payet', 'Lionel Messi', 'shooting')

#%%
#creating scatter graph of comparison of 2 different points in the same csv file 
#need to create a version where we can do a scatter plot comparing 
import matplotlib.pyplot as plt 

def scatter_graphs_comparison(stats_csv, primary_attribute, secondary_attribute):
    #replacing all inf values 
    stats_csv.replace([np.inf, -np.inf], 0, inplace=True)
    #sorting the df by primary attribute and then secondary 
    best_primary = stats_csv.sort_values([primary_attribute, secondary_attribute], ascending = False) 
    #taking the top 20 results 
    best_performers = best_primary.head(n=20)
    # open figure + axis
    fig, ax = plt.subplots()
    # plot
    ax.scatter(x=best_performers[primary_attribute],y=best_performers[secondary_attribute],c='DarkBlue')
    # set labels
    ax.set_xlabel(primary_attribute)
    ax.set_ylabel(secondary_attribute)
    
    # annotate points in axis
    for idx, row in best_performers.iterrows():
        ax.annotate(row['player'], (row[primary_attribute], row[secondary_attribute]) )
    # force matplotlib to draw the graph
        
    return plt.show()

scatter_graphs_comparison(passing_stats_2020_2021, "xa", "crosses_into_penalty_area")


#%%
#finding the correlation between 2 rows in a csv 
def correlation_between_atrributes(stats_csv, primary_attribute, secondary_attribute):
    primary_column = stats_csv[primary_attribute]
    secondary_column = stats_csv[secondary_attribute]
    correlation = primary_column.corr(secondary_column)
    return correlation 

#note: correlation is more strong the closer the number is to 1. If it is close to -1, they are negative correlated 
print(correlation_between_atrributes(passing_stats_2020_2021, "xa", "crosses_into_penalty_area"))

#%%
#creating a correlation matrix between all values 
correlation_matrix = all_2020_2021_stats.corr()
#creating a heatmap using seaborn is the next bit so you can visualize more easily 
import seaborn as sn 

sn.heatmap(correlation_matrix)
plt.show()
correlation_matrix.to_csv('correlation_stats.csv')

#%%
#One thing I noticed from the graph above is that there is quite a strong correlation between pressures in final third and xg 
#so I have elaborated on this further below 

#sorting by most pressures 
top_attack_pressures = all_2020_2021_stats.sort_values("pressures_att_3rd", ascending = False)
#getting the top 50 of these 
top_pressure_attack_performers = top_attack_pressures.head(n=50)
#now sorting by age 
potential_top_scorers = top_pressure_attack_performers.loc[(top_pressure_attack_performers['age'] <= 25)]
potential_top_scorers.to_csv('high_potential_players.csv')