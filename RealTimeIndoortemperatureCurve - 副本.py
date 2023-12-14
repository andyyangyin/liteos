from cProfile import label
from re import X
import serial
import threading
import random
import os
import math
import time
from   datetime import datetime, timedelta
import numpy as np
import json
import pandas as pd
import serial.tools.list_ports
from   PySide6.QtGui import QPixmap, QFont
from   PySide6.QtCore import Signal, Qt, QTimer, QDateTime, QThread
from   PySide6.QtWidgets import QMainWindow,QApplication,QMessageBox,QWidget,QVBoxLayout
from   PySide6 import QtCharts
from   matplotlib.figure import Figure
import matplotlib.pyplot as plt
from   matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from   threading import Thread
import mplcursors           #鼠标移动显示坐标值 需要安装 mplcursors



class MyCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = plt.figure(figsize=(749, 749), dpi=80) 
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    def clear(self): 
       self.figure.clear()   
    def plot(self, x, y,Lable):  

        plt.rcParams["font.family"]="Kaiti"       #添加可以显示中文
        plt.rcParams['axes.unicode_minus']=False  # 用来正常显示负号

        plt.title("室内实时温度曲线")  
 
        # 设置x轴和y轴的范围
        #plt.xlim(2, 8)
        plt.ylim(12, 40)

        # 设置横坐标刻度值   自定义的横坐标刻度值     
        temp = []
        for i in range(0,len(x)):
            if y[i] == 0:
                temp.append(x[i])              
        plt.xticks(temp,temp,rotation=10)

        '''
        #在某些坐标处显示 自定义文本
        for i in range(0,len(y)):
            if y[i] == 0:
                plt.text(x[i], y[i], f'({x[i]}, {y[i]})')
        '''
        plt.plot(x, y,label=Lable) 
        plt.xlabel("X")   
        plt.ylabel("y")  
        self.canvas.draw()   
        plt.legend()
        mplcursors.cursor(hover=True)  #鼠标移动显示坐标值

selectTimeFlag = 1
selectTime     = ""   
class PlotThread(threading.Thread): 
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
    def run(self):
        global selectTime
        global selectTimeFlag
        while True:
            if selectTimeFlag ==0:
                continue
            selectTimeFlag = 0
            self.canvas.clear()   

            df = pd.read_csv('./userData.csv',parse_dates=['timestamp','powerontime']) #timestamp powerontime以时间方式打开，否则excel读出来的不全
            df = df.reset_index(drop=True)
            if  1:
                if len(selectTime) <= 0:
                    now        = datetime.now()
                    selectTime = now.strftime("%Y/%m/%d %H:%M:%S")
                #按照一天的数据显示
                selectTime = selectTime.split(' ')[0]+" 00:00:00"
                start_time   = datetime.strptime(selectTime,"%Y/%m/%d %H:%M:%S")
                end_time = start_time + timedelta(days=0, hours=23,minutes=59,seconds=59)
                print("start_time:",start_time,"end_time:",end_time)
                df = df.loc[(df['powerontime'] >= start_time) & (df['powerontime'] <= end_time)]
  
            x1 = [] 
            y1 = []
            y2 = []      
            for i in range(1,len(df)):
                if  df['power'].iloc[i-1]  == 0 or df['power'].iloc[i-1]  != df['power'].iloc[i]:
                    y1.append(0)
                    y2.append(0)
                    x1.append(df['timestamp'].iloc[i] )
                else:
                    y1.append(df['indoorTemperature'].iloc[i])
                    y2.append(df['setTemperature'].iloc[i])
                    x1.append(df['timestamp'].iloc[i] )                             
            self.canvas.plot(x1,y2,"SetTemperature")
            self.canvas.plot(x1,y1,"indoorTemperature")

            for i in range(1,20):# 0.5秒钟检测一次用户是否有查询新的指令
                time.sleep(2)  
                if  selectTimeFlag == 1:
                    break



    
##----------------------------------------历史常用程序----------------------------------------
        '''
        plt.rcParams["font.family"]="Kaiti"       #添加可以显示中文
        plt.rcParams['axes.unicode_minus']=False  # 用来正常显示负号
        ax1 = plt.subplot(2,10,1)
        m = [1,2,3,4,5,6]
        n = [10,20,30,40,50,60]
        ax1.plot(m,n)
        ax1.set_title("子图1")


        ax1 = plt.subplot(2,10,2)
        m = [1,2,3,4,5,6]
        n = [10,20,30,40,50,60]
        ax1.plot(m,n)
        ax1.set_title("子图2")
        self.canvas.draw() 






        '''

