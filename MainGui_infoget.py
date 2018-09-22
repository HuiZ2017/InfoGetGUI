#!/usr/bin/env python
# encoding: utf-8
'''
@author: zhanghui
@file: MainGui_infoget.py
@time: 2018/9/21 20:40
'''

import tkinter as tk
import requests,re,threading
from bs4 import BeautifulSoup as bs
from tkinter import messagebox as msg
from tkinter import ttk,StringVar
from tkinter.ttk import Notebook
import webbrowser as wbopen
class InfoGetGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("InfoGetGUI v0.1")
        self.geometry("800x500")
        self.wm_attributes('-topmost', 1)
        #self.iconbitmap('favicon-20180922073644975.ico')
        self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.label.pack(side=tk.BOTTOM,fill=tk.X)
        self.label.config(text='by 张珲 有建议欢迎交流 Tel:+86 17673102113')
        #添加页面
        self.notebook = Notebook(self,height = 300,width = 600)
        self.HNJXWFrame = tk.Frame(self.notebook)
        self.notebook.add(self.HNJXWFrame, text="湖南省经信委")
        self.HNSTFrame = tk.Frame(self.notebook)
        self.notebook.add(self.HNSTFrame, text="湖南省科技厅")
        self.HNFGWFrame = tk.Frame(self.notebook)
        self.notebook.add(self.HNFGWFrame, text="湖南省发改委")
        self.notebook.pack(side=tk.LEFT, fill=tk.Y)
        #添加功能模块，搜索
        self.FunctionPart = tk.Frame(self, height=20, width=100)
        self.FunctionPart.pack(side=tk.RIGHT, fill=tk.Y)
        v = StringVar(self, value='请输入关键词进行检索')
        self.SearchList = tk.Entry(self.FunctionPart, width=20, font=('Arial', 10),textvariable=v)
        self.SearchList.pack(anchor=tk.SW,expand=tk.NO,fill=tk.X)
        self.SearchButton = tk.Button(self.FunctionPart, height=1, width=5, text="开始",command=self.Search)
        self.SearchButton.pack(anchor=tk.SW, expand=tk.NO, fill=tk.X)

        # #检索范围
        # self.sizeTag = tk.StringVar()
        # self.sizenumberChosen = ttk.Combobox(self.FunctionPart, width=10, textvariable=self.sizeTag)
        # self.sizenumberChosen['values'] = (list(np.arange(1,100,1)))  # 设置下拉列表的值
        # self.sizenumberChosen.current(0)
        # self.sizenumberChosen.pack()



        #初始数据
        self.INIT_Data()
        self.HNJXW['outbox'], self.HNJXW['outboxflag'] = self.INIT_outbox(self.HNJXWFrame)
        self.HNST['outbox'], self.HNST['outboxflag'] = self.INIT_outbox(self.HNSTFrame)
        self.HNFGW['outbox'], self.HNFGW['outboxflag'] = self.INIT_outbox(self.HNFGWFrame)
        self.objlist = [self.HNST, self.HNFGW, self.HNJXW]
        self.Search()
    # 初始化各种result,
    def INIT_Data(self):
        self.hnjxw_outbox_result = []
        self.hnst_outbox_result = []
        self.hnfgw_outbox_result = []
        # self.MainURL = {
        #     'hnjxw':"http://www.hnjxw.gov.cn/xxgk_71033/tzgg/",
        #     'hnst':"http://www.hnst.gov.cn/xxgk/tzgg/tzgg/",
        #     'hnfgw':"http://www.hnfgw.gov.cn/xxgk_70899/tzgg/"
        # }
        # self.SearchURL = {
        #     'hnjxw': "http://service.hunan.gov.cn/was5/web/search",#searchword: 军民融合 channelid: 258676
        #     'hnst': "http://service.hunan.gov.cn/was5/web/search",#searchword: 军民融合 channelid: 245143
        #     'hnfgw': "http://service.hunan.gov.cn/was5/web/search"#searchword: 军民融合 channelid: 272091
        # }
        self.HNST = {
            'name':'HNST',
            'MainURL':"http://www.hnst.gov.cn/xxgk/tzgg/tzgg/",
            'SearchURL':"http://service.hunan.gov.cn/was5/web/search",
            'channelid':"245143",
            'result':self.hnst_outbox_result
        }
        self.HNFGW = {
            'name':'HNFGW',
            'MainURL':"http://www.hnfgw.gov.cn/xxgk_70899/tzgg/",
            'SearchURL':"http://service.hunan.gov.cn/was5/web/search",
            'channelid':"272091",
            'result':self.hnfgw_outbox_result
        }
        self.HNJXW = {
            'name':'HNJXW',
            'MainURL':"http://www.hnjxw.gov.cn/xxgk_71033/tzgg/",
            'SearchURL':"http://service.hunan.gov.cn/was5/web/search",
            'channelid':"258676",
            'result':self.hnjxw_outbox_result
        }
    # 分有keyword和没有的，有key的已经写完了,先触发INIT_outbox，再逐一写入到各种result里
    def Search(self):
        self.Clear_outbox()
        self.Clear_data()
        self.INIT_Data()  # result都初始化
        keywords = self.SearchList.get()
        t1 = threading.Thread(target=self.subSearch,args=(keywords,))
        self.SearchButton.config(state='disabled')
        for t in [t1]:
            t.setDaemon(True)
            t.start()
    def subSearch(self,keywords):
        if keywords == "请输入关键词进行检索":
            for obj in self.objlist:
                self.initSearch(obj)
        else:
            for obj in self.objlist:
                self.keywordsSearch(keywords=keywords,key=obj)
        self.INIT_output()  # insert现有的result
        self.SearchButton.config(state='normal')

    # Search方法的keywords分支的实现
    def keywordsSearch(self,keywords,key):
        url = key['SearchURL']
        page = 1;endpage = 1
        data = {
            'channelid':key['channelid'],
            'searchword':keywords,
            'page' : page,
            'orderby': '-crtime'
        }
        response = requests.post(url,data)
        soup = bs(response.text,"html.parser")
        #获取页数
        try:
            pagesoup = soup.select('#table6 tr td a.last-page')[0]
            endpage = int(re.match('.*search.page=([0-9]*)&',pagesoup['href'])[1]) #页数
            if endpage >= 10:
                endpage = 10
        except Exception as e:
            pass
        if endpage > 1:
            while page <= endpage:
                response = requests.post(url, data)
                soup = bs(response.text, "html.parser")
                for ii in soup.select('#table2 tr td #table4 tr td'):
                    if ii:
                        try:
                            raw = ii.select('font')[2].text
                            res = '.*(20[0-9]{2}\.[0-9]{2}\.[0-9]{2}).*'
                            T = re.match(res,raw)[1]
                            for jj in ii.select('font'):
                                if jj:
                                    for kk in jj.select('a'):
                                        if kk:
                                            key['result'].append([kk.text,kk['href'],T])
                                        #kk = <a href="http://kjt.hunan.gov.cn/xxgk/gzdt/szdt/201603/t20160330_2994287.html" target="_blank">娄底：“三区”科技人才服务<font color="#FF0000">新化</font>农村电商</a>
                        except Exception as ee:
                            pass
                page+=1
                data['page'] = page
        else:
            for ii in soup.select('#table2 tr td #table4 tr td'):
                if ii:
                    try:
                        raw = ii.select('font')[2].text
                        res = '.*(20[0-9]{2}\.[0-9]{2}\.[0-9]{2}).*'
                        T = re.match(res, raw)[1]
                        for jj in ii.select('font'):
                            if jj:
                                for kk in jj.select('a'):
                                    if kk:
                                        key['result'].append([kk.text, kk['href'], T])
                                    # kk = <a href="http://kjt.hunan.gov.cn/xxgk/gzdt/szdt/201603/t20160330_2994287.html" target="_blank">娄底：“三区”科技人才服务<font color="#FF0000">新化</font>农村电商</a>
                    except Exception as ee:
                        pass

    # Search方法的nullkeys分支的实现
    def initSearch(self,obj):
        url = obj['MainURL']
        pageno = 1
        endpage = 5
        while pageno <= endpage:
            back = ''
            if pageno == 1:
                back = 'index.html'
            else:
                back = 'index'+'_'+str(pageno-1)+'.html'
            response = requests.get(url+back)
            response.encoding = 'UTF-8'
            soup = bs(response.text,"html.parser")
            #获取内容
            result = soup.select('table tbody tr')
            for ii in result:
                #ii ---> <a href="./201809/t20180918_5097173.html" target="_blank" title="2018年度省级星创天地拟认定名单公示">2018年度省级星创天地拟认定名单公示</a>
                if ii:
                    try:
                        if obj['name'] == "HNST":
                            notime = ii.select('td a')[0]
                            yestime = ii.select('td')[1].text
                            obj['result'].append([notime['title'], url + notime['href'], yestime])
                        elif obj['name'] == "HNJXW" or obj['name'] == "HNFGW":
                            notime = ii.select('td a')[0]
                            yestime = ii.select('td')[2].text
                            obj['result'].append([notime.text,url+notime['href'], yestime])
                    except Exception as e:
                        print(e)
            pageno+=1

    # Clear_outbox，再根据各种result的值，触发outbox_insert插入到各tree
    def INIT_output(self):
        #self.INIT_output(self.hnjxw_outbox,self.hnjxw_outbox_result,result)
        for obj in self.objlist:
            #self.Clear_outbox(obj)
            if obj['result']:
                for data in obj['result']:
                    #data ----> ['专家学者齐聚新化，共谋先进陶瓷产业发展', 'http://kjt.hunan.gov.cn/xxgk/gzdt/kjkx/201807/t20180724_5059758.html', '2018.07.24']
                    if data:self.outbox_insert(obj['outbox'],obj['outboxflag'],data)
            else:
                self.outbox_insert(obj['outbox'], obj['outboxflag'], ['未检索到任何内容', 'Null', 'Null'])
    def INIT_outbox(self,position):
        boxflag = 0
        obj = ttk.Treeview(position)  # 表格
        obj = ttk.Treeview(position, show='headings',height=540, columns=("a", "b", "c"))
        obj.column("a", width=490)
        obj.column("b", width=100, anchor="center")
        obj.column("c", width=0, anchor="center")
        obj.heading("a", text="文档标题（双击可打开查看详情）")
        obj.heading("b", text="发布时间")
        obj.heading("c", text="url")
        def onDBClick(event):
            try:
                item = obj.selection()[0]
                wbopen.open(obj.item(item,"values")[2])
            except Exception as e:
                msg.showerror('错误','浏览器打开失败')
            #print(obj.item(item,"values"))
        obj.bind("<Double-1>",onDBClick)
        obj.pack(side=tk.BOTTOM, anchor=tk.S, fill=tk.Y)
        return obj,boxflag
    def outbox_insert(self,obj,flag,args):
        obj.insert('', "end", text="123", values=(args[0], args[2], args[1]))
        flag += 1
    def Clear_outbox(self):
        for obj in self.objlist:
            items = obj['outbox'].get_children()
            [obj['outbox'].delete(item) for item in items]
    def Clear_data(self):
        for obj in self.objlist:
            obj['result'] = []
            obj['outboxflag'] = 0
        '''
        items = self.outbox2.get_children()
        [self.outbox2.delete(item) for item in items]
        self.outbox2Flag = 0
        msg.showinfo("提示！","已清空检索列表")
        '''

if __name__ == "__main__":
    demo1 = InfoGetGUI()
    demo1.mainloop()



    '''
    demo1.HNST['result'] ------>   [['专家学者齐聚新化，共谋先进陶瓷产业发展', 'http://kjt.hunan.gov.cn/xxgk/gzdt/kjkx/201807/t20180724_5059758.html', '2018.07.24']]
    '''