from tkinter import *
import tkinter.ttk as ttk
from tkinter.constants import *
from pandas import Series
from tkinter import messagebox
import pandas as pd
import numpy as np
import json


class VerticalScrolledFrame(ttk.Frame):
    def __init__(self, parent, **kw):
        ttk.Frame.__init__(self, parent, **kw)

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

    def __init__(self, master=None):
        super(View, self).__init__(master)
        # 初始配置

        self.fluency_of_grammar = IntVar(0)
        self.correlation = IntVar(0)
        self.accuracy = IntVar(0)
        self.comprehensive = IntVar(0)
        self.page = IntVar(0)
        self.page_num = 0
        self.idx = 0
        self.dialogs = []
        self.summaries = []
        self.data = []
        self.key = []
        self.current_id = None
        np.random.seed(1230)
        self.random = np.random.rand(100)
        # 默认从第0页开始
        self.file_score_name = "data/score/dialog.json"
        self.file_dialogs_name = "data/dialogs/dialog(1).json"
        # self.file_summary_name = "data/summary/ts.json"

        """ 初始化布局 左边的 对话区 """
        self.frame_dialog = Frame(root, width=550, bd=1, relief="sunken")
        self.frame_dialog.pack(side="left", fill="y", ipadx=10, ipady=10,
                               expand=0)

        """ summary区  """
        self.frame_title = Frame(root, height=100, bd=1, relief="sunken")
        self.frame_title.pack(side="top", fill="x", ipadx=10,
                              ipady=80,
                              expand=0)
        """ 底部的功能区 """
        self.frame_bottom = Frame(root, width=100, bd=1, relief="sunken")
        self.frame_bottom.pack(side="top", fill="both", ipadx=10,
                               ipady=10,
                               expand=True)
        """ 评分区 """
        self.frame_score = LabelFrame(self.frame_bottom, text="score", font=("微软雅黑", 10))
        self.frame_score.pack(side="top", fill="both", ipadx=10,
                              ipady=10,
                              expand=True)
        self.g1_label1 = Label(self.frame_score, text="Response", font=("微软雅黑", 12, 'bold'),
                               fg="grey")
        self.g1_label2 = Label(self.frame_score, text="very Dissatisfied \n 1", font=("  Times New roman", 10),
                               fg="grey")
        self.g1_label3 = Label(self.frame_score, text="Dissatisfied\n 2", font=("  Times New roman", 10),
                               fg="grey")
        self.g1_label4 = Label(self.frame_score, text="Middle\n 3", font=("  Times New roman", 10),
                               fg="grey")
        self.g1_label5 = Label(self.frame_score, text="Satisfied\n 4", font=("  Times New roman", 10),
                               fg="grey")
        self.g1_label6 = Label(self.frame_score, text="Very Satisfied\n 5", font=("  Times New roman", 10),
                               fg="grey")
        self.g1_label7 = Label(self.frame_score, text="语法流畅度", font=("微软雅黑", 10),
                               fg="grey")
        self.g1_label8 = Label(self.frame_score, text="相关性", font=("微软雅黑", 10),
                               fg="grey")
        self.g1_label9 = Label(self.frame_score, text="准确性", font=("微软雅黑", 10),
                               fg="grey")
        self.g1_label10 = Label(self.frame_score, text="综合评分", font=("微软雅黑", 10),
                                fg="grey")

        # 标签布局
        self.g1_label1.grid(row=0, column=0, padx=10, pady=10)
        self.g1_label2.grid(row=0, column=1, padx=10, pady=10)
        self.g1_label3.grid(row=0, column=2, padx=10, pady=10)
        self.g1_label4.grid(row=0, column=3, padx=10, pady=10)
        self.g1_label5.grid(row=0, column=4, padx=10, pady=10)
        self.g1_label6.grid(row=0, column=5, padx=10, pady=10)
        self.g1_label7.grid(row=1, column=0, padx=10, pady=10)
        self.g1_label8.grid(row=2, column=0, padx=10, pady=10)
        self.g1_label9.grid(row=3, column=0, padx=10, pady=10)
        self.g1_label10.grid(row=4, column=0, padx=10, pady=10)
        # 语法流畅单选按钮
        self.fluency_of_grammar_1 = Radiobutton(self.frame_score, variable=self.fluency_of_grammar, value=1)
        self.fluency_of_grammar_2 = Radiobutton(self.frame_score, variable=self.fluency_of_grammar, value=2)
        self.fluency_of_grammar_3 = Radiobutton(self.frame_score, variable=self.fluency_of_grammar, value=3)
        self.fluency_of_grammar_4 = Radiobutton(self.frame_score, variable=self.fluency_of_grammar, value=4)
        self.fluency_of_grammar_5 = Radiobutton(self.frame_score, variable=self.fluency_of_grammar, value=5)
        # 相关性单选按钮
        self.correlation_1 = Radiobutton(self.frame_score, variable=self.correlation, value=1)
        self.correlation_2 = Radiobutton(self.frame_score, variable=self.correlation, value=2)
        self.correlation_3 = Radiobutton(self.frame_score, variable=self.correlation, value=3)
        self.correlation_4 = Radiobutton(self.frame_score, variable=self.correlation, value=4)
        self.correlation_5 = Radiobutton(self.frame_score, variable=self.correlation, value=5)
        # 准确性单选按钮
        self.accuracy_1 = Radiobutton(self.frame_score, variable=self.accuracy, value=1)
        self.accuracy_2 = Radiobutton(self.frame_score, variable=self.accuracy, value=2)
        self.accuracy_3 = Radiobutton(self.frame_score, variable=self.accuracy, value=3)
        self.accuracy_4 = Radiobutton(self.frame_score, variable=self.accuracy, value=4)
        self.accuracy_5 = Radiobutton(self.frame_score, variable=self.accuracy, value=5)
        # 综合评分单选按钮
        self.comprehensive_1 = Radiobutton(self.frame_score, variable=self.comprehensive, value=1)
        self.comprehensive_2 = Radiobutton(self.frame_score, variable=self.comprehensive, value=2)
        self.comprehensive_3 = Radiobutton(self.frame_score, variable=self.comprehensive, value=3)
        self.comprehensive_4 = Radiobutton(self.frame_score, variable=self.comprehensive, value=4)
        self.comprehensive_5 = Radiobutton(self.frame_score, variable=self.comprehensive, value=5)
        # 单选按钮布局
        self.fluency_of_grammar_1.grid(row=1, column=1, padx=10, pady=10)
        self.fluency_of_grammar_2.grid(row=1, column=2, padx=10, pady=10)
        self.fluency_of_grammar_3.grid(row=1, column=3, padx=10, pady=10)
        self.fluency_of_grammar_4.grid(row=1, column=4, padx=10, pady=10)
        self.fluency_of_grammar_5.grid(row=1, column=5, padx=10, pady=10)

        self.correlation_1.grid(row=2, column=1, padx=10, pady=10)
        self.correlation_2.grid(row=2, column=2, padx=10, pady=10)
        self.correlation_3.grid(row=2, column=3, padx=10, pady=10)
        self.correlation_4.grid(row=2, column=4, padx=10, pady=10)
        self.correlation_5.grid(row=2, column=5, padx=10, pady=10)

        self.accuracy_1.grid(row=3, column=1, padx=10, pady=10)
        self.accuracy_2.grid(row=3, column=2, padx=10, pady=10)
        self.accuracy_3.grid(row=3, column=3, padx=10, pady=10)
        self.accuracy_4.grid(row=3, column=4, padx=10, pady=10)
        self.accuracy_5.grid(row=3, column=5, padx=10, pady=10)

        self.comprehensive_1.grid(row=4, column=1, padx=10, pady=10)
        self.comprehensive_2.grid(row=4, column=2, padx=10, pady=10)
        self.comprehensive_3.grid(row=4, column=3, padx=10, pady=10)
        self.comprehensive_4.grid(row=4, column=4, padx=10, pady=10)
        self.comprehensive_5.grid(row=4, column=5, padx=10, pady=10)

        self.entry02 = Entry(self.frame_bottom, textvariable=self.page, width=15)
        self.page_to_button = Button(self.frame_bottom, text="page to", font=("  Times New roman", 12),
                                     command=self.page_to)
        self.entry02.pack(side='left')
        self.page_to_button.pack(side='left')

        # 初始化数据
        self.insert_button()
        self.get_data_by_file()
        self.set_dialog()
        self.set_summary()
        self.max_len = len(self.dialogs)
        self.pack()

    def insert_button(self):
        model_frame = Frame(self.frame_bottom)
        model_frame.pack(side="bottom")
        # 底部功能栏的按钮
        before_button = Button(model_frame, text="<", font=("  Times New roman", 12), command=self.before)
        entry_button = Button(model_frame, text="保存", font=("  Times New roman", 12), command=self.save_score_file)
        next_button = Button(model_frame, text=">", font=("  Times New roman", 12), command=self.next)
        # 按钮定位
        before_button.grid(row=0, column=4, padx=10, pady=10)
        entry_button.grid(row=0, column=6, padx=10, pady=10)
        next_button.grid(row=0, column=8, padx=10, pady=10)

    def get_data_by_file(self):
        df = pd.read_json(self.file_dialogs_name, encoding='utf-8')
        obj = df.to_dict()
        count = 0
        for key in obj:
            for i in range(len(obj[key])):
                if key == 'body':
                    data = obj['body'][i].split('< code >')
                    dialog = []
                    if len(data) > 1:
                        dialog.append(data[0])
                        dialog.append(data[1])
                        self.dialogs.append(dialog)
                    else:
                        data = obj['body'][i].split('<SEP>')
                        for d in data:
                            dialog.append(d)
                        self.dialogs.append(dialog)
                else:
                    if count == 1:
                        if len(obj[key][i].split('\t')) > 1:
                            summary = {key: obj[key][i].split('\t')[1].split('\n')[0]}
                        else:
                            summary = {key: obj[key][i].split('\n')[0]}
                        self.summaries.append(summary)
                    else:
                        if len(obj[key][i].split('\t')) > 1:
                            self.summaries[i][key] = obj[key][i].split('\t')[1].split('\n')[0]
                        else:
                            self.summaries[i][key] = obj[key][i].split('\n')[0]
            count += 1

        with open(self.file_score_name) as file:
            text = file.read()
            if text == '':
                self.data = []
            else:
                data_set = json.loads(text)
                self.json_to_series(data_set)

    def json_to_series(self, data_set):
        new_data = []
        for data in data_set:
            score = data['score']
            data['score'] = eval(score)
            score = Series(data['score'])
            data['score'] = score
            new_data.append(data)
        self.data = new_data

    def next(self):
        if self.page_num < self.max_len:
            self.page_num += 1
            self.page.set(self.page_num)
            self.update_frame()
            if self.is_page() == -1:
                self.data.append(self.create_page())
            if self.current_id is not None:
                self.save_score()
            self.current_id = None

    def before(self):
        if self.page_num > 0:
            self.page_num -= 1
            self.page.set(self.page_num)
            self.update_frame()
            if self.is_page() == -1:
                self.data.append(self.create_page())
            if self.current_id is not None:
                self.save_score()
            self.current_id = None

    # 当文件中没有该页的值则直接创建这页的初始化值
    def create_page(self):
        score = Series([[0, 0, 0, 0]], [0])
        score = score.reindex(self.key, fill_value=[0, 0, 0, 0])
        return {'page_num': self.page_num, 'score': score}

    def set_summary(self):
        titles = self.get_summary()
        if titles is None:
            return
        self.list_frame = Listbox(self.frame_title, listvariable=StringVar(), width=200, height=400)
        self.list_frame.bind('<Button-1>', self.click_button)
        self.list_frame.pack(side="top")
        titles_values_list = self.get_random_value_list(titles, self.page_num)
        for i in range(len(titles_values_list)):
            self.list_frame.insert(i, titles_values_list[i])
        self.key = self.get_random_key_list(titles, self.page_num)
        scy = Scrollbar(self.list_frame)
        scx = Scrollbar(self.list_frame, orient=HORIZONTAL)
        scx.pack(side=BOTTOM, fill=X)
        scy.pack(side=RIGHT, fill=Y)
        self.list_frame.pack(anchor='w', expand='yes', fill=BOTH)
        scx.config(command=self.list_frame.xview)
        scy.config(command=self.list_frame.yview)
        self.list_frame.config(xscrollcommand=scx.set,
                               yscrollcommand=scy.set)

    def get_random_key_list(self, titles, i):
        random_key_list = []
        random_num = int(self.random[i] * 6)
        key_list = [v for v in titles.keys()]
        random_key_list.append(key_list[random_num % len(titles)])
        key_list.pop(random_num % len(titles))
        if len(key_list) > 1:
            random_key_list.append(key_list[int(random_num / 3)])
            key_list.pop(int(random_num / 3))
            random_key_list.append(key_list[0])
        else:
            random_key_list.append(key_list[0])
        return random_key_list

    def get_random_value_list(self, titles, i):
        random_value_list = []
        random_num = int(self.random[i] * 6)
        titles_list = [v for v in titles.values()]
        random_value_list.append(titles_list[random_num % len(titles)])
        titles_list.pop(random_num % len(titles))
        if len(titles_list) > 1:
            random_value_list.append(titles_list[int(random_num / 3)])
            titles_list.pop(int(random_num / 3))
            random_value_list.append(titles_list[0])
        else:
            random_value_list.append(titles_list[0])
        return random_value_list

    def set_dialog(self):
        dialog = self.get_dialog()
        if dialog is None:
            return
        data = dialog
        self.dialog_frame = VerticalScrolledFrame(self.frame_dialog)
        self.dialog_frame.pack(side="left", fill="y", ipadx=10, ipady=10,
                               expand=0)
        for i in range(len(data)):
            g1_label2 = Text(self.dialog_frame.interior, wrap=WORD, font=("  Times New roman", 12), width=50,
                             height=3 if (len(data[i]) / 30) < 3 else len(data[i]) / 30)
            g1_label2.insert(INSERT, data[i])
            g1_label2.grid(row=i, column=4, padx=2, pady=5)
        # g1_label1 = Text(self.dialog_frame.interior, wrap=WORD, font=("  Times New roman", 12), width=50,
        #                  height=3 if (len(data['dialog']) / 30) < 3 else len(data['dialog']) / 30)
        # g1_label1.insert(INSERT, data['dialog'])
        # g1_label1.grid(row=1, column=4, padx=2, pady=5)
        # g1_label2 = Text(self.dialog_frame.interior, wrap=WORD, font=("  Times New roman", 12), width=50,
        #                  height=3 if (len(data['code']) / 30) < 3 else len(data['code']) / 30)
        # g1_label2.insert(INSERT, data['code'])
        # g1_label2.grid(row=2, column=4, padx=2, pady=5)

    def get_summary(self):
        current_id = self.page_num
        max_len = len(self.summaries)
        if current_id < max_len:
            return self.summaries[current_id]
        return None

    def get_dialog(self):
        current_id = self.page_num
        max_len = len(self.dialogs)
        if current_id < max_len:
            return self.dialogs[current_id]
        return None
        pass

    def save_score_file(self):
        with open(self.file_score_name, "w", encoding='utf-8') as file:
            new_data = []
            for data in self.data:
                data['score'] = Series.to_json(data['score'])
                new_data.append(data)
            text = json.dumps(new_data)
            file.write(text)
            self.json_to_series(self.data)
            messagebox.showinfo("info", "保存成功")

    def page_to(self):
        self.page_num = int(self.page.get())
        self.update_frame()
        if self.is_page() == -1:
            self.data.append(self.create_page())
            self.update_score()
        pass

    def blank(self):
        pass

    def click_button(self, event):
        if len(self.list_frame.curselection()) > 0:
            if self.current_id is not None and self.current_id != int(self.list_frame.curselection()[0]):
                self.save_score()
            current = self.current_id
            self.current_id = int(self.list_frame.curselection()[0])
            if self.current_id != current:
                current_index = self.is_page()
                if current_index != -1:
                    self.idx = current_index
                    if self.data[self.idx]['score'][self.current_id] != [0, 0, 0, 0]:
                        score = self.data[self.idx]['score'][self.current_id]
                        self.fluency_of_grammar.set(score[0])
                        self.correlation.set(score[1])
                        self.accuracy.set(score[2])
                        self.comprehensive.set(score[3])
                else:
                    self.data.append(self.create_page())

    def save_score(self):
        score = [self.fluency_of_grammar.get(), self.correlation.get(), self.accuracy.get(), self.comprehensive.get()]
        self.data[self.idx]['score'][self.current_id] = score
        self.update_score()

    def update_score(self):
        self.fluency_of_grammar.set(0)
        self.correlation.set(0)
        self.accuracy.set(0)
        self.comprehensive.set(0)

    def update_frame(self):
        self.list_frame.destroy()
        self.dialog_frame.destroy()
        self.set_dialog()
        self.set_summary()

    def is_page(self):
        for i in range(len(self.data)):
            if self.data[i]['page_num'] == self.page_num:
                return i
        return -1


if __name__ == "__main__":
    root = Tk()
    root.geometry("1300x750+100+100")
    root.title("dialogs annotation")
    index = View(master=root)
    root.mainloop()
