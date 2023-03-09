import tkinter as tk
import os
from tkinter import filedialog
import random


# def select_file_names():
#     selection = filedialog.askopenfilenames(
#         filetypes=[('all files', '*.*'), ('python files', '.py')])
#     return selection
#
#
# def select_directory():
#     selection = filedialog.askdirectory()
#     return selection
#
#
# def grid_widget(widget, row, column, padx=5, pady=5, sticky=tk.W):
#     widget.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
#
#
# class Task_scheduler(object):
#     def __init__(self):
#         self.listbox_files = None
#         self.root = tk.Tk()
#         self.root.title('python 模块调度工具')
#         self.lay_widgets()
#         self.filePath = 'D:/py/dialog_GUI/data/annotations'
#         self.files = os.listdir(self.filePath)
#         self.show_files()
#
#     def lay_widgets(self):
#         # labelframe
#         self.labelframe_root = tk.LabelFrame(self.root, text='')
#         self.labelframe_root.grid(
#             row=0, column=0, padx=5, pady=5, sticky='WENS')
#         #
#         self.labelframe_button = tk.LabelFrame(self.labelframe_root, text='操作')
#         self.labelframe_button.grid(
#             row=1, column=0, padx=5, pady=5, sticky='WENS')
#         #
#         self.labelframe_listbox = tk.LabelFrame(
#             self.labelframe_root, text='文件列表')
#         self.labelframe_listbox.grid(
#             row=2, column=0, padx=5, pady=5, sticky='WENS')
#
#         # button
#
#     def add_files(self):
#         files = select_file_names()
#         for file in files:
#             print(file)
#             self.listbox_files.insert(tk.END, file)
#         pass
#
#     def del_selection(self):
#         selection = self.listbox_files.curselection()
#         for index in selection[::-1]:
#             print(index)
#             self.listbox_files.delete(index)
#         pass
#
#     def show_files(self):
#         self.listbox_files = tk.Listbox(self.labelframe_listbox,
#                                         width=80, height=5,
#                                         selectmode=tk.EXTENDED)
#
#         self.listbox_files.pack(anchor='w', expand='no', fill=tk.BOTH)
#         for file in self.files:
#             self.listbox_files.insert(tk.END, file)
#
#         button_add = tk.Button(self.labelframe_button,
#                                text='添加文件', command=self.add_files)
#         grid_widget(button_add, 0, 0)
#         button_del = tk.Button(self.labelframe_button,
#                                text='删除选中', command=self.del_selection)
#         grid_widget(button_del, 0, 1, sticky='E')
#
#
#     def start(self):
#         self.root.mainloop()
#         pass
#
#
# if __name__ == '__main__':
#     ins = Task_scheduler()
#     ins.start()
# from tkinter import *
#
# root = Tk()
# canvas=Canvas(root,width=200,height=180,scrollregion=(0,0,520,520)) #创建canvas
# canvas.place(x = 75, y = 265) #放置canvas的位置
# frame=Frame(canvas) #把frame放在canvas里
# frame.place(width=180, height=180) #frame的长宽，和canvas差不多的
# vbar=Scrollbar(canvas,orient=VERTICAL) #竖直滚动条
# vbar.place(x = 180,width=20,height=180)
# vbar.configure(command=canvas.yview)
# hbar=Scrollbar(canvas,orient=HORIZONTAL)#水平滚动条
# hbar.place(x =0,y=165,width=180,height=20)
# hbar.configure(command=canvas.xview)
# canvas.config(xscrollcommand=hbar.set,yscrollcommand=vbar.set) #设置
# canvas.create_window((90,240), window=frame)  #create_window
# root.mainloop()

# ------------------------------------------------------------------
# import tkinter as tk
#
#
# class VerticalScrolledFrame(tk.Frame):
#     """A pure Tkinter scrollable frame that actually works!
#     * Use the 'interior' attribute to place widgets inside the scrollable frame.
#     * Construct and pack/place/grid normally.
#     * This frame only allows vertical scrolling.
#     """
#
#     def __init__(self, parent, *args, **kw):
#         tk.Frame.__init__(self, parent, *args, **kw)
#
#         # Create a canvas object and a vertical scrollbar for scrolling it.
#         vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
#         vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
#         canvas = tk.Canvas(self, bd=0, highlightthickness=0,
#                            yscrollcommand=vscrollbar.set, width=1920,
#                            height=1000)  # 这里设定canvas的大小是frame内界面的大小，如果frame内定义的子项的大小超过了canvas的大小，则滚动条生效
#         canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
#         vscrollbar.config(command=canvas.yview)
#
#         # Reset the view
#         canvas.xview_moveto(0)
#         canvas.yview_moveto(0)
#
#         # Create a frame inside the canvas which will be scrolled with it.
#         self.interior = interior = tk.Frame(canvas)
#         interior_id = canvas.create_window(0, 0, window=interior,
#                                            anchor=tk.NW)
#
#         # Track changes to the canvas and frame width and sync them,
#         # also updating the scrollbar.
#         def _configure_interior(event):
#             # Update the scrollbars to match the size of the inner frame.
#             size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
#             canvas.config(scrollregion="0 0 %s %s" % size)
#             if interior.winfo_reqwidth() != canvas.winfo_width():
#                 # Update the canvas's width to fit the inner frame.
#                 canvas.config(width=interior.winfo_reqwidth())
#
#         interior.bind('<Configure>', _configure_interior)
#
#         def _configure_canvas(event):
#             if interior.winfo_reqwidth() != canvas.winfo_width():
#                 # Update the inner frame's width to fill the canvas.
#                 canvas.itemconfigure(interior_id, width=canvas.winfo_width())
#
#         canvas.bind('<Configure>', _configure_canvas)
#
# if __name__ == '__main__':
#     top = tk.Tk()
#     frame = VerticalScrolledFrame(top)
#     frame.pack()
#     subFrames = tk.Frame(frame.interior, width=200, height=200, padx=5, pady=5)#注意这里会定义frame内子项的宽、高，注意父节点要设置为frame.interior
#     top.mainloop()


# !/user/bin/env Python3
# -*- coding:utf-8 -*-


# import tkinter as tk
# from tkinter import filedialog, dialogs
# import os
#
# window = tk.Tk()
# window.titles('窗口标题')  # 标题
# window.geometry('500x500')  # 窗口尺寸
#
# file_path = ''
#
# file_text = ''
#
# text1 = tk.Text(window, width=50, height=10, bg='orange', font=('Arial', 12))
# text1.pack()
#
#
# def open_file():
#     '''
#     打开文件
#     :return:
#     '''
#     global file_path
#     global file_text
#     file_path = filedialog.askopenfilename(titles=u'选择文件', initialdir=(os.path.expanduser('H:/')))
#     print('打开文件：', file_path)
#     if file_path is not None:
#         with open(file=file_path, mode='r+', encoding='utf-8') as file:
#             file_text = file.read()
#
#
# def save_file():
#     global file_path
#     global file_text
#     file_path = filedialog.asksaveasfilename(titles=u'保存文件')
#     print('保存文件：', file_path)
#     file_text = text1.get('1.0', tk.END)
#     if file_path is not None:
#         with open(file=file_path, mode='a+', encoding='utf-8') as file:
#             file.write(file_text)
#         text1.delete('1.0', tk.END)
#         dialogs.Dialog(None, {'titles': 'File Modified', 'text': '保存完成', 'bitmap': 'warning', 'default': 0,
#                              'strings': ('OK', 'Cancle')})
#         print('保存完成')
#
#
# bt1 = tk.Button(window, text='打开文件', width=15, height=2, command=open_file)
# bt1.pack()
# bt2 = tk.Button(window, text='保存文件', width=15, height=2, command=save_file)
# bt2.pack()
#
# window.mainloop()  # 显示

print(random.randint(0, 1))

