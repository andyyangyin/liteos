
#     Important:
#     用下面命令把ui界面生成python程序文件
#     pyside6-uic ui.ui -o ui_form.py
from ui_form import Ui_Dialog
import sys
import serial
import threading
import random
import os
import math
import time
from datetime import datetime
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
ser= serial.Serial()
port_list = serial.tools.list_ports.comports()   

#include 外部函数 
import RealTimeIndoortemperatureCurve 
from   RealTimeIndoortemperatureCurve     import*
from   SteadyIndoorTemperature            import*
from   uart                               import*
from   init                               import*  
class MainWindow(QMainWindow):
    def __init__(self):       
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)    
        #init load uart serial list   
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.ui.SerialSelcet.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.ui.SerialSelcet.addItem(port[0])
        if len(self.Com_Dict) == 0:
            msg_box = QMessageBox(QMessageBox.Warning, '提示', '无串口')
            msg_box.exec_()
        self.ui.serialSelectButton.clicked.connect(self.serialSelectButton_click)
        self.ui.ConfirmPushButton.clicked.connect(self.ConfirmPushButton_click)                 #确认选择日期按钮    
        self.ui.horizontalScrollBar.valueChanged.connect(self.on_scrollbar_value_changed)

        #init ui
        self.ui.indoorTempLabel.setText("23")
        self.ui.hotColdLabel.setText("--")
        self.ui.SetTempLabel.setText ("26")
        #init 温度室内温度曲线
        self.canvas = MyCanvas(self)
        self.ui.layout.addWidget(self.canvas)
        self.thread = PlotThread(self.canvas)
        self.thread.start()

        self.thread1= threading.Thread(target=self.threadUartRcv)
        self.thread1.start()

        self.thread3= threading.Thread(target=self.ThreadTmainloop)
        self.thread3.start()
    def on_scrollbar_value_changed(self):       
        print("horizontalScrollBar_changeL",self.ui.horizontalScrollBar.value())        

    def ThreadTmainloop(self):
        print("run ThreadTmainloop!!!")  
        while True:
              time.sleep(1)            
    def threadUartRcv(self):
        print("run threadUartRcv!!!")  
        uart_rcv(ser)

    def ConfirmPushButton_click(self):              #确认选择日期按钮     
        RealTimeIndoortemperatureCurve.selectTime = str(self.ui.SelectDateTime.text())    
        RealTimeIndoortemperatureCurve.selectTimeFlag = 1
        #readbin(ser)
        doRule()

    def serialSelectButton_click(self):                #串口选择确认按钮
        selected_item = self.ui.SerialSelcet.currentText()         
        if  self.ui.serialSelectButton.text() == "打开串口":            
            ser.port = selected_item 
            ser.baudrate = 115200    
            try:        
                ser.open()
                self.ui.serialSelectButton.setText("关闭串口")
            except:
                QMessageBox.critical(self, "Port Error","串口打开失败")    
        else:
            try:                
                ser.close()
                self.ui.serialSelectButton.setText("打开串口")
            except:
                QMessageBox.critical(self, "Port Error","串口关闭失败")  

    def closeEvent(self, event):
        try:
            self.ThreadTmainloop.stop()
            self.threadUartRcv.stop()           
            ser.close()
            print("关闭串口成功")
        except:
            print("关闭串口失败")
            event.accept()
if __name__ == "__main__":
    print("***************************************************")
    print("*                                                 *")
    print("*                                                 *")
    print("*                                                 *")
    print("*                                                 *")
    print("             PC端测试软件版本号V1.0                 " )  
    print("*                                                 *")
    print("*                                                 *")
    print("*                                                 *")
    print("*                                                 *")
    print("***************************************************")
    init()
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())





 








