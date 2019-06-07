from tkinter import *
import tkinter
import os
import sys
import win32api
import win32con
import win32gui_struct
import spider

'''class GUI(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.helloLabel = Label(self, text='Hello, world!')
        self.helloLabel.pack()
        self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.pack()

app = GUI()
app.master.title('hello world')
app.mainloop()'''


def start_button_click(event):
    if startButton['state'] == tkinter.NORMAL:
        startButton['state'] = tkinter.DISABLED
        stopButton['state'] = tkinter.NORMAL


def stop_button_click(event):
    if stopButton['state'] == tkinter.NORMAL:
        stopButton['state'] = tkinter.DISABLED
        startButton['state'] = tkinter.NORMAL


def open_button_click(event):
    spider.run()


# GUI setting
win = tkinter.Tk()

ws = win.winfo_screenwidth()  # 显示器宽
hs = win.winfo_screenheight()  # 显示器高
defWidth = 400
defHeight = 100
x = (ws/2) - (defWidth/2)
y = (hs/2) - (defHeight/2)
win.geometry('%dx%d+%d+%d' % (defWidth, defHeight, x, y))
win.minsize(defWidth, defHeight)
win.maxsize(defWidth, defHeight)
win.title('NGA沙雕图爬虫 by 玉米狂人赫鲁晓夫')

startButton = Button(win, text='启动', width=10, state=tkinter.NORMAL)
startButton.place(x=50, y=35)
startButton.bind('<Button-1>', start_button_click)

stopButton = Button(win, text='停止', width=10, state=tkinter.DISABLED)
stopButton.place(x=160, y=35)
stopButton.bind('<Button-1>', stop_button_click)

openButton = Button(win, text='打开文件夹', width=10)
openButton.place(x=270, y=35)
openButton.bind('<Button-1>', open_button_click)

label = Label(win, text='未运行').place(x=180, y=5)

win.mainloop()

