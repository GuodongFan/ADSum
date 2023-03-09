import urllib.request
import urllib.parse
import json
import tkinter as tk
import tkinter.messagebox

url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'


def fanyi():
    content = sr.get()

    data = {}
    data['i'] = content
    data['from'] = 'AUTO'
    data['to'] = 'AUTO'
    data['smartresult'] = 'dict'
    data['client'] = 'fanyideskweb'
    data['salt'] = '15613765644784'
    data['sign'] = '5caabbf646f6585277b7cebf45f18244'
    data['ts'] = '1561376564478'
    data['bv'] = '6074bfcb52fb292f0428cb1dd669cfb8'
    data['doctype'] = 'json'
    data['version'] = '2.1'
    data['keyfrom'] = 'fanyi.web'
    data['action'] = 'FY_BY_REALTlME'

    data = urllib.parse.urlencode(data).encode('utf-8')

    r = urllib.request.urlopen(url, data)
    html = r.read().decode('utf-8')

    target = json.loads(html)

    jieguo = target['translateResult'][0][0]['tgt']

    xs.insert(tk.END, '{}'.format(jieguo))
    xs.see(tk.END)
    xs.update()
    # tkinter.messagebox.showwarning('翻译结果', '{}'.format(jieguo))
    xs.insert(tk.END, '*********翻译完成，清空输入框重新输入<>如需复制，点击内容Ctrl+C即可*********')
    xs.see(tk.END)
    xs.update()


def ml():
    quit()


#  tk.messagebox.showwarning("抱歉", "目前该功能正在完善中")


def ml2():
    xs.delete(0, tk.END)


fy = tk.Tk()  # yy为Tk类型
fy.geometry('463x350')  # 设置界面大小

fy.title('王牌翻译器1.0（Roud）')  # 界面主题（左上角）

label = tk.Label(fy, text='请输入需要翻译的内容：')  # 界面内文本显示
label.grid(row=0, column=0, sticky='w', padx=5)  # 文本位置

sr = tk.Entry(fy, width=37)  # 界面输入框
sr.grid(row=0, column=1, columnspan=2, sticky='w')  # 输入框位置,W为西，E为东

xs = tk.Listbox(fy, width=65, heigh=15)  # 显示框大小
xs.grid(row=1, columnspan=3, sticky='w')
'''
源代码来源：Roud    更多详情  请在CSDN搜索博主：101岁咳血敲码
感谢 有道翻译 对本程序的支持
'''

# def ml1():
#     tkinter.messagebox.showwarning('警告','尚在开发中')


b1 = tkinter.Button(fy, text='确认', command=fanyi, width=10)
b1.grid(row=2, column=0, sticky='w')

b2 = tkinter.Button(fy, text='清空', command=ml2, width=10)
b2.grid(row=2, column=1, sticky='w')

b2 = tkinter.Button(fy, text='退出', command=ml, width=10)
b2.grid(row=2, column=2, sticky='e')

fy.mainloop()
# coding=utf-8
# import numpy as np
# import PIL.ImageFile as ImageFile
# import cv2
# import math
# import random
# import time
#
# # 免费代理IP不能保证永久有效，如果不能用可以更新
# # http://www.goubanjia.com/
# proxy_list = [
#     '183.95.80.102:8080',
#     '123.160.31.71:8080',
#     '115.231.128.79:8080',
#     '166.111.77.32:80',
#     '43.240.138.31:8080',
#     '218.201.98.196:3128'
# ]
#
# # 收集到的常用Header
# my_headers = [
#     "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
#     "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
#     'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
#     'Opera/9.25 (Windows NT 5.1; U; en)',
#     'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
#     'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
#     'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
#     'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
#     "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
#     "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
# ]
#
#
# def getTile(url):
#     # 每次执行前先暂停t秒
#     time.sleep(t)
#
#     # 随机选择IP、Header
#     proxy = random.choice(proxy_list)
#     header = random.choice(my_headers)
#
#     print
#     proxy, 'sleep:', t, header
#
#     # 基于选择的IP构建连接
#     urlhandle = ulb.ProxyHandler({'http': proxy})
#     opener = ulb.build_opener(urlhandle)
#     ulb.install_opener(opener)
#
#     # 用urllib2库链接网络图像
#     response = ulb.Request(url)
#
#     # 增加Header伪装成浏览器
#     response.add_header('User-Agent', header)
#
#     try:
#         # 打开网络图像文件句柄
#         fp = ulb.urlopen(response)
#
#         # 定义图像IO
#         p = ImageFile.Parser()
#
#         # 开始图像读取
#         while 1:
#             s = fp.read(1024)
#             if not s:
#                 break
#             p.feed(s)
#
#         # 得到图像
#         im = p.close()
#
#         # 将图像转换成numpy矩阵
#         arr = np.array(im)
#         return arr
#
#     except ulb.HTTPError, e:
#         print
#         e.code, e.reason
#
#         # 遇到异常返回256*256的黑色图片
#         arr = np.zeros((256, 256, 3), np.uint8)
#         return arr
#
#
# # 由x、y、z计算瓦片行列号
# def calcXY(lat, lon, z):
#     x = math.floor(math.pow(2, int(z) - 1) * ((lon / 180.0) + 1))
#     tan = math.tan(lat * math.pi / 180.0)
#     sec = 1.0 / math.cos(lat * math.pi / 180.0)
#     log = math.log(tan + sec)
#     y = math.floor(math.pow(2, int(z) - 1) * (1 - log / math.pi))
#     return int(x), int(y)
#
#
# # 字符串度分秒转度
# def cvtStr2Deg(deg, min, sec):
#     result = int(deg) + int(min) / 60.0 + float(sec) / 3600.0
#     return result
#
#
# # 获取经纬度
# def getNum(str):
#     split = str.split(',')
#     du = split[0].split('°')[0]
#     fen = split[0].split('°')[1].split('\'')[0]
#     miao = split[0].split('°')[1].split('\'')[1].split('"')[0]
#     split1 = cvtStr2Deg(du, fen, miao)
#     du = split[1].split('°')[0]
#     fen = split[1].split('°')[1].split('\'')[0]
#     miao = split[1].split('°')[1].split('\'')[1].split('"')[0]
#     split2 = cvtStr2Deg(du, fen, miao)
#     return split1, split2
#
#
# # 获取经纬度
# def getNum2(str):
#     split = str.split(',')
#     split1 = float(split[0].split('N')[0])
#     split2 = float(split[1].split('E')[0])
#     return split1, split2
#
#
# # 用户输入更新后的IP文件，如果没有则用代码中的默认IP
# ip_path = raw_input("Input the path of IP list file(input \'no\' means use default IPs):\n")
# # 判断是否输入IP文件
# if ip_path != 'no':
#     proxy_list = []
#     file = open(ip_path)
#     lines = file.readlines()
#     for line in lines:
#         proxy_list.append(line.strip('\n'))
#     print
#     proxy_list.__len__(), 'IPs are loaded.'
#
# # 输入两次请求间的暂停时间
# t = 0.1
# t = input("Input the interval time(second) of requests(e.g. 0.1):\n")
#
# # 输入影像层数
# z = 18
# z = raw_input("Input image level(0-18):\n")
#
# # 输入左上角点经纬度并计算行列号
# lt_raw = raw_input("Input lat & lon at left top(e.g. 30.52N,114.36E):\n")
# lt_lat, lt_lon = getNum2(lt_raw)
# lt_X, lt_Y = calcXY(lt_lat, lt_lon, z)
#
# # 输入右下角点经纬度并计算行列号
# rb_raw = raw_input("Input lat & lon at right bottom(e.g. 30.51N,114.37E):\n")
# rb_lat, rb_lon = getNum2(rb_raw)
# rb_X, rb_Y = calcXY(rb_lat, rb_lon, z)
#
# # 计算行列号差值及瓦片数
# cols = rb_X - lt_X
# rows = rb_Y - lt_Y
# tiles = cols * rows
# count = 0
#
# # 判断结果是否合理
# if tiles <= 0:
#     print
#     'Please check your input.'
#     exit()
# print
# tiles.__str__() + ' tiles will be downloaded.'
#
# # 输入保存路径
# base = raw_input("Input save path:\n")
#
# print
# 'Now start...'
#
# # 循环遍历，下载瓦片
# for i in range(rows):
#     for j in range(cols):
#         # 拼接url
#         url = 'http://mt2.google.cn/vt/lyrs=s&hl=zh-CN&gl=CN&x=' + (j + lt_X).__str__() + '&y=' + (
#                 i + lt_Y).__str__() + '&z=' + z.__str__()
#         # 拼接输出路径
#         path = base + '\\' + z.__str__() + '_' + (j + lt_X).__str__() + '_' + (i + lt_Y).__str__() + '.jpg'
#         # 获取瓦片
#         tile = getTile(url)
#         # 保存瓦片
#         cv2.imwrite(path, tile)
#         # 计数变量增加
#         count = count + 1
#         # 输出进度信息
#         print(round((float(count) / float(tiles)) * 100, 2)).__str__() + " % finished"