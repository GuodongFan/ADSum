import shutil
from tkinter import *
from tkinter import messagebox
import json
import tkinter.ttk as ttk
from tkinter.constants import *
import os
import urllib.request
import urllib.parse
import numpy as np
from tkinter import filedialog

url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'


def select_file_names():
    selection = filedialog.askopenfilenames(
        filetypes=[('all files', '*.*'), ('python files', '.py')])
    return selection


def translate(text):
    data = {'i': text, 'from': 'AUTO', 'to': 'AUTO', 'smartresult': 'dict', 'client': 'fanyideskweb',
            'salt': '15613765644784', 'sign': '5caabbf646f6585277b7cebf45f18244', 'ts': '1561376564478',
            'bv': '6074bfcb52fb292f0428cb1dd669cfb8', 'doctype': 'json', 'version': '2.1', 'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTlME'}

    data = urllib.parse.urlencode(data).encode('utf-8')

    r = urllib.request.urlopen(url, data)
    html = r.read().decode('utf-8')

    target = json.loads(html)

    jieguo = target['translateResult'][0][0]['tgt']

    return '{}'.format(jieguo)


def select_directory():
    selection = filedialog.askdirectory()
    return selection


def grid_widget(widget, row, column, padx=5, pady=5, sticky=W):
    widget.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)


class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """

    def __init__(self, parent, **kw):
        ttk.Frame.__init__(self, parent, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        scrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        scrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)


class View(Frame):
    count = 0

    def __init__(self, master=None):
        super(View, self).__init__(master)
        # 初始配置

        self.seed = 1024
        self.num = 2000
        self.file_annotations_name = "data/annotations/annotation_ts_2.json"
        self.file_dialogs_name = "data/dialogs/ts.json"
        self.file_titles_name = "data/titles/ts.json"

        self.file_path = ""
        np.random.seed(self.seed)
        self.random = np.random.rand(self.num)
        self.flag = 0
        self.ids = []
        self.files = []
        self.select_file_name = StringVar()
        self.var01 = StringVar()
        self.var02 = IntVar()
        self.context_menu = Menu(root)
        """ 左边文件选择列表 """
        self.frame_file = Frame(root, width=0, bd=0, relief="sunken")
        self.frame_file.pack(side="left", fill="y", ipadx=10, ipady=10,
                             expand=True)
        """ 初始化布局 左边的 对话区 """
        self.frame_dialog = Frame(root, width=550, bd=1, relief="sunken")
        self.frame_dialog.pack(side="left", fill="y", ipadx=10, ipady=10,
                               expand=0)

        """ 主题区  """
        self.frame_title = Frame(root, height=500, bd=1, relief="sunken")
        self.frame_title.pack(side="top", fill="x", ipadx=10,
                              ipady=80,
                              expand=0)
        """ 底部的功能区 """
        self.frame_bottom = Frame(root, width=100, bd=1, relief="sunken")
        self.frame_bottom.pack(side="top", fill="both", ipadx=10,
                               ipady=10,
                               expand=True)

        # self.list_frame = Listbox(self.frame_title, listvariable=StringVar(), width=200, height=400)
        # self.list_frame.bind('<Button-1>', self.click_button)
        # self.list_frame.pack(side="top")

        self.frame_bottom_top = LabelFrame(self.frame_bottom, text="status", font=("  Times New roman", 14))
        self.frame_bottom_top.pack(side="top")
        self.g1_label1 = Label(self.frame_bottom_top, text="label: not annotations", font=("  Times New roman", 14),
                               fg="grey")
        self.labelframe_listbox = LabelFrame(self.frame_file, text='文件操作')
        # self.labelframe_listbox.pack(side="top", fill="both", ipadx=10,
        #                              ipady=10,
        #                              expand=True)
        self.listbox_files = Listbox(self.labelframe_listbox,
                                     width=30, height=5,
                                     selectmode=EXTENDED)

        self.listbox_files.pack(anchor='w', expand='yes', fill=BOTH)
        self.model_frame = Frame(self.frame_file)

        # 初始化数据
        self.dialogs = []
        self.titles = []
        self.data = []
        self.current_id = 0
        self.recommend_titles = None
        self.current_idx = -1
        self.max_len = 0
        self.annotation_list = []
        if self.count == 0:
            self.set_data()
            self.count += 1

        # 菜单栏组件
        self.menu_widget()
        self.set_file_frame()
        # self.insert_files_button()
        self.insert_button()
        self.bottom_edit_entry()
        self.to_page()
        self.show_select_box()
        self.pack()

    def set_data(self):
        with open(self.file_dialogs_name) as file:
            text = file.read()
            if text == '':
                self.dialogs = []
            else:
                self.dialogs = json.loads(text)

        with open(self.file_titles_name) as file:
            text = file.read()
            if text == '':
                self.titles = []
            else:
                self.titles = json.loads(text)

        with open(self.file_annotations_name) as file:
            text = file.read()
            if text == '':
                self.data = []
            else:
                self.data = json.loads(text)

        with open("data/status.json") as file:
            text = file.read()
            if text == '':
                self.status_data = {"select_title": 0, "update_title": 0, "update_self": 0, "bad_title": 0,
                                    "file_name": self.file_titles_name}
                self.status_data_list = []
                self.status_data_list.append(self.status_data)
            else:
                self.status_data_list = json.loads(text)
                self.set_status_data(self.status_data_list)

        # 当前状态
        self.dialogs = self.update_data(self.dialogs)
        self.titles = self.update_data(self.titles)
        self.current_id = 0
        self.recommend_titles = None
        self.current_idx = -1
        self.max_len = len(self.dialogs)
        self.set_annotations()
        self.set_dialog()
        self.set_title()
        self.set_status_statistics()

    def save_json(self, data):
        with open(self.file_annotations_name, "w", encoding='utf-8') as file:
            text = json.dumps(data)
            file.write(text)
        with open("./data/status.json", "w", encoding='utf-8') as file:
            for i in range(len(self.status_data_list)):
                if self.status_data_list[i]["file_name"] == self.file_titles_name:
                    self.status_data_list[i] = self.status_data
                    text = json.dumps(self.status_data_list)
                    file.write(text)
                    break

    def menu_widget(self):
        # 创建主菜单栏
        menu_bar = Menu(root)
        # 创建子菜单栏
        menu_file = Menu(menu_bar)
        menu_edit = Menu(menu_bar)
        menu_help = Menu(menu_bar)

        # 将子菜单加入到主菜单栏
        menu_bar.add_cascade(label="File(F)", menu=menu_file)
        menu_bar.add_cascade(label="Edit(E)", menu=menu_edit)
        menu_bar.add_cascade(label="Help(H)", menu=menu_help)

        # 添加菜单项
        # 文件菜单
        menu_file.add_command(label="new", accelerator="ctrl+n", command=self.blank)
        menu_file.add_command(label="Open", accelerator="ctrl+o", command=self.open_file_edit)
        menu_file.add_command(label="Close", accelerator="ctrl+c", command=self.close_file_edit)
        menu_file.add_separator()  # 添加分割线
        menu_file.add_command(label="Quit", accelerator="ctrl+q", command=root.destroy)
        # help菜单
        menu_help.add_command(label="useful_num", accelerator="ctrl+u", command=self.get_useful_num)

        # 将主菜单栏加到根窗口
        root["menu"] = menu_bar
        # 创建上下菜单
        self.context_menu.add_command(label="", command=self.create_context_menu)

    def open_file_edit(self):

        self.labelframe_listbox.pack(side="top", fill="both", ipadx=10,
                                     ipady=10,
                                     expand=True)
        self.insert_files_button()

    def close_file_edit(self):
        file_annotations_name = self.file_annotations_name
        file_dialogs_name = self.file_dialogs_name
        file_titles_name = self.file_titles_name
        for widget in root.winfo_children():
            widget.destroy()
        self.__init__(root)
        self.file_annotations_name = file_annotations_name
        self.file_dialogs_name = file_dialogs_name
        self.file_titles_name = file_titles_name
        self.set_data()

    def get_dialog(self):
        current_id = self.current_id
        max_len = len(self.dialogs)
        if current_id < max_len:
            return self.dialogs[current_id]
        return None

    def set_dialog(self):
        dialog = self.get_dialog()
        if dialog is None:
            return
        data = dialog['data']
        data_len = len(data)
        self.dialog_frame = VerticalScrolledFrame(self.frame_dialog)
        self.dialog_frame.pack(side="left", fill="y", ipadx=10, ipady=10,
                               expand=0)
        for i in range(data_len):
            g1_label1 = Label(self.dialog_frame.interior, text=data[i]['name'] + ":", font=(" Times New roman", 14))
            g1_label1.grid(row=i, column=0)
            g1_label3 = Label(self.dialog_frame.interior, text=data[i]['time'], font=("  Times New roman", 10))
            g1_label3.grid(row=i, column=0, sticky=S)
            g1_label2 = Text(self.dialog_frame.interior, wrap=WORD, font=("  Times New roman", 13), width=50,
                             height=3 if (len(data[i]['text']) / 30) < 3 else len(data[i]['text']) / 30)
            g1_label2.insert(INSERT, data[i]['text'])
            # translate(data[i]['text']) + "--" +
            g1_label2.grid(row=i, column=4, padx=2, pady=5)

    def get_titles(self):
        current_id = self.current_id
        max_len = len(self.titles)
        if current_id < max_len:
            self.recommend_titles = []
            self.recommend_titles.extend(self.titles[current_id]['titles'])
            for i in range(len(self.annotation_list)):
                for j in range(len(self.annotation_list[i])):
                    if self.annotation_list[i][j]["id"] == current_id:
                        self.recommend_titles.append(self.annotation_list[i][j])
                        self.flag += 1
                        # del self.titles[current_id]['titles'][
                        #     len(self.recommend_titles) - len(self.annotation_list) - 1:len(self.recommend_titles) - 1]
                        break
            return self.recommend_titles
        return None

    def click_button(self, event):
        if len(self.list_frame.curselection()) > 0:
            self.current_idx = int(self.list_frame.curselection()[0])
            if self.current_idx < len(self.recommend_titles) - len(self.annotation_list):
                self.var01.set(self.recommend_titles[self.current_idx])
            else:
                self.var01.set(self.recommend_titles[self.current_idx]['title'])
                self.current_idx = self.recommend_titles[self.current_idx]['titles_index']

    def set_title(self):
        titles = self.get_titles()
        if titles is None:
            return
        self.list_frame = Listbox(self.frame_title, listvariable=StringVar(), width=300, height=400, font=("  Times New roman", 13))
        self.list_frame.bind('<Button-1>', self.click_button)
        self.list_frame.pack(side="top")
        if self.flag > 0:
            for i, title in enumerate(titles):
                if i < len(titles) - self.flag:
                    # translate(title)
                    self.list_frame.insert(i, title)
                else:
                    self.list_frame.insert(i, title['title'])
                    if title['type'] == 1:
                        self.list_frame.itemconfig(i, bg="yellow")
                    elif title['type'] == 2:
                        self.list_frame.itemconfig(i, bg="sky blue")
                    elif title['type'] == 3:
                        self.list_frame.itemconfig(i, bg="sea green")
                    else:
                        self.list_frame.itemconfig(i, bg="red")
            self.flag = 0
        else:
            for i, title in enumerate(titles):
                self.list_frame.insert(i, title)

        scy = Scrollbar(self.list_frame)
        scx = Scrollbar(self.list_frame, orient=HORIZONTAL)

        scx.pack(side=BOTTOM, fill=X)
        scy.pack(side=RIGHT, fill=Y)
        self.list_frame.pack(anchor='w', expand='yes', fill=BOTH)

        scx.config(command=self.list_frame.xview)
        scy.config(command=self.list_frame.yview)

        self.list_frame.config(xscrollcommand=scx.set,
                               yscrollcommand=scy.set)

    def update_frame(self):
        self.current_idx = -1
        self.dialog_frame.destroy()
        self.list_frame.destroy()
        self.g1_label1.destroy()
        self.g1_label2.destroy()
        self.g1_label3.destroy()
        self.var01.set("")
        self.var02.set(self.current_id)
        self.set_dialog()
        self.set_title()
        self.set_annotations()
        # self.show_select_box()
        self.set_status_statistics()

    def next(self):
        if self.current_id < self.max_len:
            self.current_id += 1
            self.update_frame()
            self.count += 1
            # print(str(self.titles[self.current_id]['id']) +":" + str(self.dialogs[self.current_id]['id']))

    def before(self):
        if self.current_id > 0:
            self.current_id -= 1
            self.update_frame()

    def text(self):
        if self.entry01.get() != '':
            one = {"id": self.current_id, "title": self.entry01.get(), "status": 0, "type": self.status_add(),
                   "dialog_id": self.titles[self.current_id]['id'], "titles_index": self.current_idx}
            if self.filter_data(one):
                self.data.append(one)
                self.update_frame()
        else:
            messagebox.showinfo("info", "输入内容不为空")

    def status_add(self):
        if self.current_idx < len(self.recommend_titles) - len(self.annotation_list):
            if self.current_idx == -1:
                self.status_data["update_self"] += 1
                status_type = 1
            elif self.recommend_titles[self.current_idx] == self.entry01.get():
                self.status_data["select_title"] += 1
                status_type = 3
            else:
                self.status_data["update_title"] += 1
                status_type = 2
            self.save_json(self.data)
            return status_type
        else:
            if self.current_idx == -1:
                self.status_data["update_self"] += 1
                status_type = 1
            elif self.recommend_titles[self.current_idx]['title'] == self.entry01.get() and \
                    self.recommend_titles[self.current_idx]['type'] == 3:
                self.status_data["select_title"] += 1
                status_type = 3
            else:
                self.status_data["update_title"] += 1
                status_type = 2
            self.save_json(self.data)
            return status_type

    def status_des(self, status_type):
        if status_type == 1:
            self.status_data["update_self"] -= 1
        elif status_type == 3:
            self.status_data["select_title"] -= 1
        elif status_type == 2:
            self.status_data["update_title"] -= 1
        else:
            self.status_data["bad_title"] -= 1

    def insert_button(self):
        model_frame = Frame(self.frame_bottom)
        model_frame.pack(side="bottom")
        # 底部功能栏的按钮
        previous_button = Button(model_frame, text="before", font=("  Times New roman", 14), command=self.before)
        next_button = Button(model_frame, text="next", font=("  Times New roman", 14), command=self.next)
        entry_button = Button(model_frame, text="update", font=("  Times New roman", 14), command=self.text)
        pass_button = Button(model_frame, text="pass", font=("  Times New roman", 14), command=self.pass_this)
        # 按钮定位
        previous_button.grid(row=0, column=0, padx=10, pady=10)
        next_button.grid(row=0, column=4, padx=10, pady=10)
        entry_button.grid(row=0, column=8, padx=10, pady=10)
        pass_button.grid(row=0, column=12, padx=10, pady=10)

    def bottom_edit_entry(self):
        model_frame = Frame(self.frame_bottom)
        model_frame.pack(side="top")

        after_label = Label(model_frame, text="update to:")
        after_label.pack()

        self.entry01 = Entry(model_frame, textvariable=self.var01, width=70, font=("  Times New roman", 13))
        self.entry01.pack()

    def create_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def pass_this(self):
        one = {"id": self.current_id, "title": self.entry01.get(), "status": 1, "type": 4,
               "dialog_id": self.titles[self.current_id]['id'], "titles_index": self.current_idx}
        if self.filter_data(one):
            self.data.append(one)
        self.status_data["bad_title"] += 1
        self.save_json(self.data)
        self.current_id += 1
        self.update_frame()

    def blank(self):
        pass

    def filter_data(self, one):
        if len(self.data) > 0:
            for i in range(len(self.data)):
                if self.data[i]["id"] == one['id']:
                    self.status_des(self.data[i]["type"])
                    self.data[i] = one
                    return False
        return True

    def set_annotations(self):
        for i in range(len(self.data)):
            if self.current_id == self.data[i]["id"]:
                self.var01.set(self.data[i]["title"])
                self.set_status_label(self.data[i]["status"])
                return
        self.set_status_label(2)

    def set_status_label(self, status):
        if status == "0":
            self.g1_label1 = Label(self.frame_bottom_top, text="label: normal annotations",
                                   font=("  Times New roman", 12), fg='green')
            self.g1_label1.grid(row=0, column=12, padx=10, pady=10)
        elif status == "1":
            self.g1_label1 = Label(self.frame_bottom_top, text="label: bad annotations",
                                   font=("  Times New roman", 12), fg="red")
            self.g1_label1.grid(row=0, column=12, padx=10, pady=10)
        else:
            self.g1_label1 = Label(self.frame_bottom_top, text="label: not annotations",
                                   font=("  Times New roman", 12), fg="grey")
            self.g1_label1.grid(row=0, column=12, padx=10, pady=10)

    def set_status_statistics(self):
        self.g1_label2 = Label(self.frame_bottom_top,
                               text="total:(" + str(len(self.dialogs)) + ")   finished:(" + str(
                                   len(self.data)) + ")", font=("  Times New roman", 12))
        self.g1_label3 = Label(self.frame_bottom_top,
                               text="Edit by Oneself:(" + str(
                                   self.status_data["update_self"]) + ")\t\nSelect & Edit:(" + str(
                                   self.status_data["update_title"]) + ")\t\nSelect Recommendations:(" + str(
                                   self.status_data["select_title"]) + ")\t\nPass:(" + str(
                                   self.status_data["bad_title"]
                               ) + ")\t\ndialog:[" + self.file_dialogs_name + "]\t\ntitle:[" + self.file_titles_name + "]\t\nannotation:[" + self.file_annotations_name + "]\n", font=("  Times New roman", 12))
        self.g1_label2.grid(row=1, column=12, padx=10, pady=10)
        self.g1_label3.grid(row=2, column=12, padx=10, pady=10)

    # 返回抽样,略微效率高一些,适合数据量大只抽小部分
    def update_data(self, data_input):
        if self.num < len(data_input):
            data_output = []
            data_size = len(data_input)
            for i in range(self.num):
                index_id = int(self.random[i] * data_size)
                if index_id < data_size:
                    data_output.append(data_input[index_id])
            return data_output
        else:
            messagebox.showinfo("info", "抽样数量大于文本数量")

    # 不放回抽样,抽取的数据不重复,适合抽样数据和元数据量数据级相同或相差不大
    def update_data_not_repeat(self, data_input):
        data_size = len(data_input)
        if self.num < len(data_input):
            data_output = []
            for i in range(self.num):
                index_id = int(self.random[i] * data_size)
                data_output.append(data_input[index_id])
                data_size -= 1
                data_input.pop(index_id)
            return data_output
        else:
            messagebox.showinfo("info", "抽样数量大于文本数量")

    def to_page(self):
        model_frame = Frame(self.frame_bottom)
        model_frame.pack(side="top")
        after_label = Label(model_frame, text="page to:")
        after_label.pack()
        self.entry02 = Entry(model_frame, textvariable=self.var02, width=70)
        self.page_to_button = Button(model_frame, text="page to", font=("  Times New roman", 12), command=self.page_to)
        self.entry02.pack()
        self.page_to_button.pack()

    def page_to(self):
        page = int(self.entry02.get())
        print(self.num)
        if page < self.num:
            self.current_id = page
            self.update_frame()
        else:
            messagebox.showinfo("info", "page out index!")

    def init_files_name(self):
        pass

    def insert_files_button(self):
        self.model_frame.pack(side="top")
        # 底部功能栏的按钮
        dialog_button = Button(self.model_frame, text="dialog", font=("  Times New roman", 10),
                               command=lambda: self.select_file_type(1))
        title_button = Button(self.model_frame, text="title", font=("  Times New roman", 10),
                              command=lambda: self.select_file_type(2))
        annotation_button = Button(self.model_frame, text="annotation", font=("  Times New roman", 10),
                                   command=lambda: self.select_file_type(3))
        recycle_button = Button(self.model_frame, text="recycle", font=("  Times New roman", 10),
                                command=lambda: self.select_file_type(4))
        dialog_button.grid(row=0, column=0, padx=10, pady=10)
        title_button.grid(row=0, column=2, padx=10, pady=10)
        annotation_button.grid(row=0, column=4, padx=10, pady=10)
        recycle_button.grid(row=0, column=6, padx=10, pady=10)

    def select_file_type(self, file_type):
        if file_type == 1:
            self.file_path = "data/dialogs"
        elif file_type == 2:
            self.file_path = "data/titles"
        elif file_type == 3:
            self.file_path = "data/annotations"
        else:
            self.file_path = "data/recycle"
        self.update_files_list()

    def set_file_frame(self):
        group = Frame(self.labelframe_listbox)
        group.pack(side="bottom")
        button_add = Button(group, text='添加文件', command=self.add_files)
        button_del = Button(group, text='删除文件', command=self.del_selection)
        button_sle = Button(group, text='选择文件', command=self.sel_selection)
        button_edit = Button(group, text='添加注解', command=self.input_annotations)

        button_add.grid(row=0, column=0, padx=10, pady=10)
        button_del.grid(row=0, column=2, padx=10, pady=10)
        button_sle.grid(row=0, column=4, padx=10, pady=10)
        button_edit.grid(row=0, column=6, padx=10, pady=10)
        pass

    def update_files_list(self):
        self.files = os.listdir(self.file_path)
        self.listbox_files.delete(0, END)
        for file in self.files:
            self.listbox_files.insert(END, file)

    def add_files(self):
        files = select_file_names()
        for file in files:
            filename = self.insert_file_info(file)
            self.listbox_files.insert(END, filename)
        pass

    def del_selection(self):
        selection = self.listbox_files.curselection()
        for file_index in selection[::-1]:
            current_file_path = self.file_path + "/" + self.files[file_index]
            if self.file_path == "data/recycle":
                os.remove(current_file_path)
            else:
                self.move_recycle(current_file_path)
            self.listbox_files.delete(file_index)
        pass

    def sel_selection(self):
        if len(self.listbox_files.curselection()) != 1:
            messagebox.showinfo("info", "too many or too less file")
        else:
            selection = self.listbox_files.curselection()[0]
            current_file_path = self.file_path + "/" + self.files[selection]
            if self.file_path == "data/dialogs":
                self.file_dialogs_name = current_file_path
                self.update_dialog()
                messagebox.showinfo("info", "会话文件切换为" + current_file_path)
            elif self.file_path == "data/titles":
                self.file_titles_name = current_file_path
                self.update_title()
                messagebox.showinfo("info", "标题文件切换为" + current_file_path)
            else:
                self.file_annotations_name = current_file_path
                self.update_annotation()
                messagebox.showinfo("info", "标注文件切换为" + current_file_path)
            self.update_frame()
            # os.remove(current_file_path)

    def update_dialog(self):
        with open(self.file_dialogs_name) as file:
            text = file.read()
            if text == '':
                self.dialogs = []
            else:
                self.dialogs = json.loads(text)
            self.dialogs = self.update_data(self.dialogs)

    def update_title(self):
        with open(self.file_titles_name) as file:
            text = file.read()
            if text == '':
                self.titles = []
            else:
                self.titles = json.loads(text)
            self.titles = self.update_data(self.titles)
            self.update_status()

    def update_annotation(self):
        with open(self.file_annotations_name) as file:
            text = file.read()
            if text == '':
                self.data = []
            else:
                self.data = json.loads(text)
                self.update_status_data()

    def update_status(self):
        with open("./data/status.json") as file:
            text = file.read()
            if text == '':
                self.status_data = {"select_title": 0, "update_title": 0, "update_self": 0, "bad_title": 0,
                                    "file_name": self.file_titles_name}
            else:
                self.set_status_data(self.status_data_list)

    def set_status_data(self, status_list):
        for i in range(len(status_list)):
            if status_list[i]["file_name"] == self.file_titles_name:
                self.status_data = status_list[i]
                return
        self.status_data = {"select_title": 0, "update_title": 0, "update_self": 0, "bad_title": 0,
                            "file_name": self.file_titles_name}
        self.status_data_list.append(self.status_data)

    def insert_file_info(self, file_name):
        with open(file_name) as file:
            text = file.read()
            if text == '':
                messagebox.showinfo("info", "file is empty!")
            else:
                (path, filename) = os.path.split(file_name)
                with open(self.file_path + "/" + filename, "w", encoding='utf-8') as w_file:
                    w_file.write(text)
                    return filename

    def input_annotations(self):
        selection = self.listbox_files.curselection()
        self.annotation_list = []
        for file_index in selection[::-1]:
            current_file_path = self.file_path + "/" + self.files[file_index]
            with open(current_file_path) as file:
                text = file.read()
                if text == '':
                    self.annotation_list = []
                else:
                    self.annotation_list.append(json.loads(text))
                self.update_frame()

    def move_recycle(self, file_name):  # 移动函数
        (path, filename) = os.path.split(file_name)
        shutil.move(file_name, "data/recycle/" + filename)  # 移动文件

    def show_select_box(self):
        files_box = os.listdir("data/dialogs")
        files_titles = os.listdir("data/titles")
        select_box_frame = ttk.Combobox(self.frame_file, width=12, height=8, textvariable=self.select_file_name,
                                        postcommand=self.update_file_by_box)
        select_box_frame.pack(side="top")
        select_box_frame["values"] = list(set(files_box).intersection(set(files_titles)))
        select_box_frame.bind("<<ComboboxSelected>>", self.update_file_by_box)

    def update_file_by_box(self, *args):
        if self.select_file_name.get() != '':
            self.file_dialogs_name = "data/dialogs" + "/" + self.select_file_name.get()
            self.update_dialog()
            (path, filename) = os.path.split(self.file_dialogs_name)
            self.file_titles_name = "data/titles" + "/" + filename
            self.update_title()
            self.update_frame()
            # messagebox.showinfo("info", "update file to " + filename)

    def get_useful_num(self):
        bad_num = 0
        for i in range(len(self.data)):
            if self.data[i]['type'] == 4:
                bad_num += 1
        messagebox.showinfo("info", "useful_num=" + str(len(self.data) - bad_num))

    def update_status_data(self):
        bad_num = 0
        update_self_num = 0
        update_title_num = 0
        select_title_num = 0
        self.num = len(self.data)
        for i in range(self.num):
            if self.data[i]['type'] == 1:
                update_self_num += 1
            elif self.data[i]['type'] == 2:
                update_title_num += 1
            elif self.data[i]['type'] == 3:
                select_title_num += 1
            else:
                bad_num += 1
        self.status_data = {"select_title": select_title_num, "update_title": update_title_num,
                            "update_self": update_self_num, "bad_title": bad_num,
                            "file_name": self.file_titles_name}


if __name__ == "__main__":
    root = Tk()
    root.geometry("1300x750+100+100")
    root.title("dialogs annotation")
    index = View(master=root)
    root.mainloop()
