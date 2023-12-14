from pickle import GLOBAL
import sys
import serial
import threading
import random
import os
import math
import time
from datetime import datetime, timedelta
import numpy as np
import json
import pandas as pd
import serial.tools.list_ports
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Signal, Qt, QTimer, QDateTime, QThread
from PySide6.QtWidgets import QMainWindow,QApplication,QMessageBox,QWidget,QVBoxLayout
from PySide6 import QtCharts
from PySide6.QtWidgets import QApplication, QMainWindow, QScrollBar
from PySide6.QtCore import Qt

from   matplotlib.figure import Figure
import matplotlib.pyplot as plt
from   matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from   threading import Thread
################   核密度运算    ########################
def gaussian_kernel(x:float)->float:
    return (1/math.sqrt(2*math.pi))*math.exp(-0.5*(x**2))

def calculate_kde(x:float, data:list)->float:
    bandwidth=1.05*np.std(data)*(len(data)**(-1/5))
    N=len(data)
    prop=0
    if len(data)==0:
        return 0
    for i in range(len(data)):
        prop += gaussian_kernel((x-data[i])/bandwidth)
    prop /= (N*bandwidth)
    return prop
def calculate_temperature(data:list)->float:
    tmp3 = [i + random.random()/10.0 for i in data]##增加精度，避免数据相同，无法拟合
    tmp3 = tmp3[3:] ##去掉前3个点
    x = np.linspace(min(tmp3), max(tmp3), 30)
    y = [calculate_kde(x[i], tmp3) for i in range(x.shape[0])]##密度估计
    m = y.index(max(y)) ##密度最大索引
    steady_temperature = x[m]##稳态温度
    return steady_temperature
################   核密度运算    ########################
def powerontime(df):
    df = df.reset_index(drop=True)
    if (len(df) == 0):
        return df

    powerontime = datetime.strptime(str(df['timestamp'].iloc[0]),"%Y-%m-%d %H:%M:%S")
    end_time   = datetime.strptime(str(df['timestamp'].iloc[-1]),"%Y-%m-%d %H:%M:%S")
    if end_time - powerontime < timedelta(minutes=60):
        return df

    #筛选出前20分钟,运行时长最长的设定温度
    powerontime = datetime.strptime(str(df['timestamp'].iloc[0]),"%Y-%m-%d %H:%M:%S")
    for i in range(0,len(df)):
        end_time   = datetime.strptime(str(df['timestamp'].iloc[i]),"%Y-%m-%d %H:%M:%S")
        if  end_time - powerontime > timedelta(minutes=20):
            break
    v = df.loc[(df['timestamp'] >= powerontime) & (df['timestamp'] <= end_time)]    
    counts  = v['settingtemperature'].value_counts(normalize=False, sort=True, ascending=False, bins=None, dropna=True ) #对temp一维数组 进行数据排序 以降序  且看那个数字出现的频率越高
    df['hotCold']  = (counts.index.tolist()[0])
    hotColdTemp = counts.index.tolist()[0]
    #print("速冷/速热设定温度是:",hotColdTemp)

    #运行20分后,运行时长最长的设定温度 即恒定设定温度
    v = df.loc[(df['timestamp'] >= end_time)]  
    counts  = v['settingtemperature'].value_counts(normalize=False, sort=True, ascending=False, bins=None, dropna=True ) #对temp一维数组 进行数据排序 以降序  且看那个数字出现的频率越高
    df['hdsettingtemperature']    = (counts.index.tolist()[0])
    hdwdTemp = counts.index.tolist()[0]
    #print("恒定设定温度:",hdwdTemp)
    if abs(hotColdTemp - hdwdTemp) > 1:
        df['FlghotCold']    = 1
        #print("用户有速冷/速热需求")

   
    for i in range(1,len(df)):
        temp = abs(df['currenttemperature'].iloc[i] - df['currenttemperature'].iloc[i-1] )/10   
        df.loc[i, 'TempSpeed']  = temp 
          
    return df
def sn(df):
    df = df.reset_index(drop=True)
    #print("sn:",df['sn'].iloc[0])
    df = df.groupby(['powerontime']).apply(powerontime)
    return df

def doRule():
    print("***************************************************")
    print("*                                                 *")
    print("             基于用户数据的自动控制规则              " )  
    print("*                                                 *")
    print("***************************************************")
    try:
        with open('./userData.csv', 'r') as file:
            df = pd.read_csv(file, parse_dates=['timestamp','powerontime'])   
            df = df.reset_index(drop=True)
            df['hotCold']       = 0
            df['FlghotCold']    = 0
            df['hdsettingtemperature'] = 0
            df['TempSpeed']     = 0.0   
            df['FLAG_01']          = 0            
            #df.drop(['area', 'kjsnwd', 'kjswwd', 'month', 'day', 'sd', 'outroomhuanjing', 'kd1', 'kd2','kdn',"open"], axis=1, inplace=True)    
            #df.dropna(inplace=True)   #去掉空白项
            print("分析中......")
            df = df.groupby(['sn']).apply(sn)
            df.to_csv('./userdata111111.csv',index=False)

            print("分析完毕......")
            return
            print(df['powerontime'].iloc[0])
            print(df['timestamp'].iloc[0])
            #df.loc[0, 'timestamp']  = 1    	                 #写timestamp这列的第一个数据
            print("读取某一系列的前面3个数据   到一维数组	可以用 	 前闭后开:",df['timestamp'][:3])
            print("读取某一系列的前面3个数据   到一维数组	可以用 	 前闭后开:",df['timestamp'][3:])
            print("筛选开机时间等于2023-10-5 12:00:00的数据:",df[df['powerontime']=='2023-11-05 12:00:00'])
    except Exception as e:
        print(f"...........doRule Error reading CSV file: {e}")



