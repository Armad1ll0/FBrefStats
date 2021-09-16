# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 10:00:53 2021

@author: amill
"""

import pandas as pd 
from sklearn import linear_model 
import numpy as np 
import matplotlib.pyplot as plt 

#importing data 
shooting_stats_2020_2021 = pd.read_csv('FB_ref_shooting_stats_2020_2021.csv')
#cleaning data 
shooting_stats_2020_2021.replace([np.inf, -np.inf], 0, inplace=True)

#%%
#this cell creates a basic linear regression based off of xg to goals. Just an example to see if everything works 
#loading in the data for a linear regression model 
X = shooting_stats_2020_2021['xg'].values
Y = shooting_stats_2020_2021['goals'].values

length = len(X)

X = X.reshape(length, 1)
Y = Y.reshape(length, 1)

regr = linear_model.LinearRegression()
regr.fit(X, Y)

plt.scatter(X, Y,  color='black')
plt.plot(X, regr.predict(X), color='blue', linewidth=3)
plt.xticks(('XG'))
plt.yticks(('Goals'))
plt.show()

#%% 
#now a more complicated model based off of shots on target and shot distance 
#do a train test split and train it on shot on target, shot distance and xg. 

#creating a sub set of the variables we want 
columns = ['shots_on_target', 'average_shot_distance', 'xg']
df = shooting_stats_2020_2021[['shots_on_target', 'average_shot_distance', 'xg']]
#adding a bias column 
#print(df.head())

features = ['shots_on_target', 'average_shot_distance']
target = 'xg'

X = df[features].values.reshape(-1, len(features))
y = df[target].values

ols = linear_model.LinearRegression()
model = ols.fit(X, y)

coeffs = model.coef_
intercept = model.intercept_

print(coeffs[0])
fig_df = df[features].values
fig_df[0] = fig_df[0]*coeffs[0]
fig_df[1] = fig_df[1]*coeffs[1]

predicted_xg = []
for row in fig_df:
    predicted_xg.append(row[0] + row[1] + intercept)

y = y.tolist()
plt.scatter(predicted_xg, y, s=4)
plt.xlabel('Predicted Xg')
plt.ylabel('Actual Xg')
plt.title('Predicted Xg using Shots on Target and Shot Distance \n Linear Regression Model vs Actual Xg')
plt.show()

#print(predicted_xg)
#ax.scatter(sequence_containing_x_vals, sequence_containing_y_vals, sequence_containing_z_vals)
#plt.show()

#%%
#doing a trin test split to get a better idea of the accuracy 
from sklearn.model_selection import train_test_split

y = df[target].values
X = df[features].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

lm = linear_model.LinearRegression()
model = lm.fit(X_train, y_train)
predictions = lm.predict(X_test)

plt.scatter(y_test, predictions)
plt.xlabel('Actual Values')
plt.ylabel('Predictions')

print('Score:', model.score(X_test, y_test))

#%%
#merging shot creation and passing for later xa work 
#importing data 
passing_stats_2020_2021 = pd.read_csv('FB_ref_passing_stats_2020_2021.csv')
shot_creation_stats_2020_2021 = pd.read_csv('FB_ref_shot_creation_stats_2020_2021.csv')
#cleaning data 
passing_stats_2020_2021.replace([np.inf, -np.inf], 0, inplace=True)
shot_creation_stats_2020_2021.replace([np.inf, -np.inf], 0, inplace=True)
#merging the columns I need 
cols = shot_creation_stats_2020_2021.columns.difference(passing_stats_2020_2021.columns)
create_pass = passing_stats_2020_2021.join(shot_creation_stats_2020_2021[cols])

#%%
features = ['passes_into_final_third', 'passes_into_penalty_area', 'crosses_into_penalty_area', 'sca_defense', 'sca_dribbles', 'sca_fouled', 'sca_passes_dead', 'sca_passes_live', 'progressive_passes']
target = 'xa'
from sklearn.model_selection import train_test_split

y = create_pass[target].values
X = create_pass[features].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

lm = linear_model.LinearRegression()
model = lm.fit(X_train, y_train)
xa_coeffs = model.coef_
predictions = lm.predict(X_test)

plt.scatter(y_test, predictions)
plt.xlabel('Actual Values')
plt.ylabel('Predictions')

print('Score:', model.score(X_test, y_test))

#%%
#finding all combos of features without repitions 
import time as time 
import itertools
start = time.time()

list_of_features = []
for L in range(0, len(features)+1):
    for subset in itertools.combinations(features, L):
        list_of_features.append(subset)

list_of_features.pop(0)
list_of_features = [list(elem) for elem in list_of_features]

average_test_acc = []
samples = 100
for j in list_of_features:
    test_acc = []
    features = j
    for i in range(samples):
        y = create_pass[target].values
        X = create_pass[features].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        lm = linear_model.LinearRegression()
        model = lm.fit(X_train, y_train)
        xa_coeffs = model.coef_
        predictions = lm.predict(X_test)
        
        # plt.scatter(y_test, predictions)
        # plt.xlabel('Actual Values')
        # plt.ylabel('Predictions')
        
        test_acc.append(
        model.score(X_test, y_test))
    average_test_acc.append(np.mean(test_acc))

max_value = max(average_test_acc)
max_index = average_test_acc.index(max_value)
end = time.time()
print('The best features for xa are: ', list_of_features[max_index])
print('It produces an average test accuracy of ', max_value)
print('This program took ' + str(end-start) + ' to run.')

#%%
#seeing if I can do exactly the same thing but with assists  
start = time.time()
target = 'assists'

list_of_features = []
for L in range(0, len(features)+1):
    for subset in itertools.combinations(features, L):
        list_of_features.append(subset)

list_of_features.pop(0)
list_of_features = [list(elem) for elem in list_of_features]

average_test_acc = []
samples = 100
for j in list_of_features:
    test_acc = []
    features = j
    for i in range(samples):
        y = create_pass[target].values
        X = create_pass[features].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        lm = linear_model.LinearRegression()
        model = lm.fit(X_train, y_train)
        xa_coeffs = model.coef_
        predictions = lm.predict(X_test)
        
        # plt.scatter(y_test, predictions)
        # plt.xlabel('Actual Values')
        # plt.ylabel('Predictions')
        
        test_acc.append(
        model.score(X_test, y_test))
    average_test_acc.append(np.mean(test_acc))

max_value = max(average_test_acc)
max_index = average_test_acc.index(max_value)
end = time.time()
print('The best features for xa are: ', list_of_features[max_index])
print('It produces an average test accuracy of ', max_value)
print('This program took ' + str(end-start) + ' to run.')

#%%
#this section will model xg from player to player as opposed to on average shooting position. Effectively this gives an indicator of best finishers 



