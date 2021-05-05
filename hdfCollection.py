#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  4 11:26:27 2021

@author: akitokosugi
"""

import os
import pandas as pd
import tkinter
import tkinter.filedialog

# In[File loading]:

# Read old file    
root = tkinter.Tk()
root.withdraw()
fTyp = [("","*h5")]
iDir = os.path.abspath(os.path.dirname('__file__'))
filePath_old = tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
print(filePath_old)

df_old = pd.read_hdf(filePath_old, 'df_with_missing')


# Read old file    
root = tkinter.Tk()
root.withdraw()
fTyp = [("","*h5")]
iDir = os.path.abspath(os.path.dirname('__file__'))
filePath_new = tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
print(filePath_new)

df_new = pd.read_hdf(filePath_new, 'df_with_missing')
   
    
# In[1]: Correction

df_collect = df_new.copy()
    
# MP xy
temp = df_old.iloc[:,0:2]
df_collect.iloc[:,0:2] = temp.values
# PIP xy
temp = df_old.iloc[:,2:4]
df_collect.iloc[:,3:5] = temp.values
# DIP xy
temp = df_old.iloc[:,4:6]
df_collect.iloc[:,6:8] = temp.values
# Pellet xy
temp = df_old.iloc[:,6:8]
df_collect.iloc[:,9:11] = temp.values


# In[2]: Save

fName = os.path.basename(os.path.splitext(filePath_old)[0])
fNameExt = os.path.basename(os.path.splitext(filePath_old)[1])
pathTemp = [os.path.dirname(os.path.splitext(filePath_old)[0]),fName + '_correct'+fNameExt]
filePath_collect = os.path.join(*pathTemp)

df_collect.to_hdf(filePath_collect, key='df_with_missing', mode ='w')
