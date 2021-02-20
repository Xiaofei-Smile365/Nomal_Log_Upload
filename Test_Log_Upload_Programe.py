# -*- coding: utf-8 -*-
"""
@Time    : 2020/9/7 8:11
@Author  : Xiaofei
@Contact : xiaofei.smile365@Gmail.com
@File    : Test_Log_Upload_Programe.py
@Version : 1.0
@IDE     : PyCharm
@Source  : python -m pip install *** -i https://pypi.tuna.tsinghua.edu.cn/simple
"""

import sys  # 载入sys函数库
import os  # 载入os函数库

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']  # 手动添加相关环境变量，以解决PyQt5打包报错的异常
from PyQt5 import QtCore  # 导入PyQt5函数库中的QtCore
from PyQt5.QtWidgets import *  # 在Qt5中使用的基本的GUI窗口控件都在PyQt5.QtWidgets模块中
from PyQt5.QtGui import QFont  # 导入PyQt5.QtGui中的QFont
from PyQt5.QtCore import Qt  # 导入PyQt5.QtGui中的Qt

import datetime  # 导入datetime函数库，用于时间相关的运用
from watchdog.observers import Observer  # 导入watchdog函数库，用于监控系统文件夹是否有文件生成、删除、修改等
from watchdog.events import *  # 同上

import socket  # 用于获取本机MAC地址、IP等信息
from ftplib import *  # 用于打开FTP服务器、上传文件等操作
import csv  # 用于进行CSV文档等基本操作

global label_title  # 声明全局变量，用于数字界面显示等
global label_qty  # 同上
global qty  # 同上
global status  # 同上


def ftp_connect(host, username, password):
    ftp = FTP()  # 对FTP函数进行实例化
    ftp.connect(host=host)  # Link到FTP服务器
    ftp.login(username, password)  # 使用用户名&密码登录
    ftp.cwd("RPDO/")  # 定位到相应目录
    print(ftp.getwelcome())
    return ftp


def upload_file(remote_path, local_path):
    try:
        try:
            ftp = ftp_connect("10.5.95.141", "User-AI", "python")  # 打开FTP服务器
            buf_size = 1024  #设定缓存
            fp = open(local_path, 'rb')  # 打开被创建的文件
            ftp.storbinary('STOR %s' % remote_path, fp, buf_size)  # 上传文件到FTP服务器
            ftp.set_debuglevel(0)  # 设定debug模式0
            fp.close()  # 关闭被创建的文件
            ftp.quit()  # 退出FTP服务器
            return 1  # 返回 1，便于判断是否上传成功
        except:
            ftp = ftp_connect("172.31.98.2", "User-AI", "python")  # 同上
            buf_size = 1024
            fp = open(local_path, 'rb')
            ftp.storbinary('STOR %s' % remote_path, fp, buf_size)
            ftp.set_debuglevel(0)
            fp.close()
            ftp.quit()
            return 1
    except:
        return 0


class MainWindow(QMainWindow):
    global label_title  # 声明全局变量
    global label_qty
    global qty
    global status

    def __init__(self, parent=None):  # 基础窗口控件QWidget类是所有用户界面对象的基类， 所有的窗口和控件都直接或间接继承自QWidget类。
        global label_title  # 声明全局变量
        global qty
        global status

        super(MainWindow, self).__init__(parent)  # 使用super函数初始化窗口

        self.setWindowTitle('ND 测试站点Log档上传程式')  # 设定窗口控件的标题
        self.setFixedSize(400, 300)  # 设定窗口的尺寸

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)  # 设定界面始终位于前置界面

        status = self.statusBar()  # 定义状态栏

        qty = 0  # 定义上抛数量
        self.ui_element()  # 定义界面基本控件
        self.layout_setup()  # 定义界面布局
        try:  # 运行以下代码段，如果报错则运行except内的代码
            self.watchdog(path="C:/")
        except:
            print("The Device may be no C Disk")
        try:  # 同上
            self.watchdog(path="D:/")
        except:
            print("The Device may be no D Disk")
        print("上传程式已启动 in %s\n" % datetime.datetime.now())  # 通过print显示代码启动信息，便于调试
        status.showMessage("上传程式已启动 in %s\n" % datetime.datetime.now(), 3000)  # 显示状态栏信息

    def ui_element(self):
        global label_title  # 声明全局变量
        global label_qty  # 同上

        label_title = QLabel(self)  # 定义QLabel，用于界面上显示文字
        label_title.setText('<b>IDLE<b>')  # 设定QLabel的文本信息
        label_title.setAlignment(Qt.AlignCenter)  # 设定文本信息居中
        label_title.setStyleSheet('color: rgb(0, 0, 0)')  # 设定文本信息颜色
        label_title.setFont(QFont('SanSerif', 100))  # 设定文本信息字体
        label_title.setFixedSize(400, 150)  # 设定控件的尺寸
        self.h_box_title = QHBoxLayout()  # 定义水平布局
        self.h_box_title.addWidget(label_title)  # 设定布局内控件

        label_qty = QLabel(self)  # 同上
        label_qty.setText(str(qty))
        label_qty.setAlignment(Qt.AlignCenter)
        label_qty.setStyleSheet('color: rgb(0, 0, 0)')
        label_qty.setFont(QFont('SanSerif', 50))
        label_qty.setFixedSize(400, 100)
        self.h_box_qty = QHBoxLayout()
        self.h_box_qty.addWidget(label_qty)

    def layout_setup(self):
        self.v_box = QVBoxLayout()  # 定义垂直布局
        self.v_box.addLayout(self.h_box_qty)  # 向布局内添加子布局
        self.v_box.addLayout(self.h_box_title)  # 向布局内添加子布局

        self.widget = QWidget()  # 定义一个控件
        self.widget.setLayout(self.v_box)  # 设定控件的布局
        self.setCentralWidget(self.widget)  # 设定界面的中心布局

    def watchdog(self, path):
        # 自定义处理类
        class MyHandler(FileSystemEventHandler):
            global label_title  # 声明全局变量
            global label_qty
            global qty
            global status

            def on_created(self, event):
                global label_title  # 声明全局变量
                global label_qty
                global qty

                try:  # 加入try异常处理机制，防止程式中断
                    config_list = []  # 定义列表list，存储config信息
                    with open('./config.csv', 'r') as f:  # 打开config文件
                        reader = csv.reader(f)  # 读取文件
                        for i in reader:  # 通过for循环写入到列表
                            config_list.append(i[1])

                    site = config_list[0]  # 站点
                    line = config_list[1]  # 线体
                    station = config_list[2]  # 工位
                    type = config_list[3]  # 类型
                except:
                    site = "???"  # 站点
                    line = "???"  # 线体
                    station = "???"  # 工位
                    type = "???"  # 类型
                    pass

                my_name = socket.gethostname()  # 获取本机名称
                my_ip = socket.gethostbyname(my_name)  # 获取本机IP

                now_time_for_rename = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))  # 获取当前时间并对时间进行格式化
                path_name = os.path.basename(event.src_path)  # 获取被修改的文件名及其路径
                created_file_path = event.src_path  # 被创建的文件
                created_file_type = os.path.splitext(created_file_path)[-1][1:]  # 获取被清洗文件文件的后缀名
                if created_file_type == type.upper() or created_file_type == type.lower():
                    print("\n###############################################################")
                    print("数据文件[%s]被创建 in %s" % (event.src_path, datetime.datetime.now()))  # 在此函数内定义需触发的事件

                    result = upload_file(site + "_" + line + "_" + station + "_" + my_name + '_' + my_ip + '_' + now_time_for_rename + '_' + path_name, event.src_path)

                    if result == 1:
                        print("该文件上抛成功\n")
                        label_title.setText('<b>OK<b>')  # 设定界面文本信息
                        label_title.setStyleSheet('color: rgb(0, 255, 0)')  # 设定界面文本信息颜色
                        qty = qty + 1
                        label_qty.setText(str(qty))  # 设定界面数量显示
                        label_qty.setStyleSheet('color: rgb(0, 255, 0)')  # 设定界面文本信息颜色
                    if result == 0:
                        print("该文件上抛失败\n")
                        label_title.setText('<b>NG<b>')
                        label_title.setStyleSheet('color: rgb(255, 0, 0)')
                        qty = qty
                        label_qty.setText(str(qty))
                        label_qty.setStyleSheet('color: rgb(255, 0, 0)')

        event_handler = MyHandler()  # 实例化MyHandler类
        observer = Observer()  # 开启相关服务
        observer.schedule(event_handler, path, recursive=True)  # 设定监控路径
        observer.start()  # 开启监控


def ui_restart(app_restart, form_restart):
    form_restart.show()  # 使用show()方法将窗口控件显示在屏幕上
    if app.exec_() == 0:
        ui_restart(app_restart, form_restart)
        sys.exit()
    sys.exit(app.exec_())  # 进入该程序的主循环;使用sys.exit()方法的退出可以保证程序完整的结束，在这种情况下系统的环境变量会记录程序是如何退出的；如果程序运行成功，exec_()的返回值为0，否则为非0


if __name__ == '__main__':  # 如果直接运行此python文件，此处为程序入口；如果作为函数库导入到其他文件，则以下内容不执行
    app = QApplication(sys.argv)  # 每一个PyQt5程序中都需要有一个QApplication对象，QApplication类包含在QTWidgets模块中，sys.argv是一个命令行参数列表；Python脚本可以从Shell中执行，比如双击*.py文件，通过参数来选择启动脚本的方式
    form = MainWindow()
    form.show()  # 使用show()方法将窗口控件显示在屏幕上

    if app.exec_() == 0:
        ui_restart(app, form)  # UI automatic restart
        sys.exit()
    sys.exit(app.exec_())  # 进入该程序的主循环;使用sys.exit()方法的退出可以保证程序完整的结束，在这种情况下系统的环境变量会记录程序是如何退出的；如果程序运行成功，exec_()的返回值为0，否则为非0

    pass

