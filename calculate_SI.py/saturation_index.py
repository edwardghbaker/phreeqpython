#%% Imports 
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from phreeqpython import PhreeqPython
#%% Define functions 

def replace_neg_with_zero(df):
    return df.where(df>0,0)

#%% Import chemical data

data=pd.read_csv('data/1_AG_SUP_Hidroquimica.csv')
df = data[[i for i in data.columns if '_dis_' in i]]

#%% Column rename dict 
keys = list(df.columns)
values = [i.split('_dis_')[0].capitalize() for i in keys]
for i in values:
    if i == 'Sio2':
        values[values.index(i)] = 'SiO2'

col_rename_dict = {keys[i]:values[i] for i in range(len(keys))}

df = replace_neg_with_zero(df)
df = df.rename(columns=col_rename_dict)
#%% 
def calculate_saturation_index(sr=df.iloc[0].T):
    pp = PhreeqPython()
    s1 = pp.add_solution_simple(sr.to_dict(),units='mg')
    return s1.phases

calculate_saturation_index()

#%%

pp = PhreeqPython()

s1 = pp.add_solution_simple({'NaHCO3':2.0},units='mg')

s1.phases

#%%
'''
I need to find the default volume of the solution so i can calculate the mg/l for each element/compound

'''

