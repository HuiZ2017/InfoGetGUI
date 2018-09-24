#!/usr/bin/env python
# encoding: utf-8
'''
@author: zhanghui
@file: MainGui_infoget.py
@time: 2018/9/24 22:40
'''

import tkinter as tk
import requests,re,threading,json
from bs4 import BeautifulSoup as bs
from tkinter import messagebox as msg
from tkinter import ttk,StringVar
from tkinter.ttk import Notebook
import webbrowser as wbopen
class InfoGetGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("InfoGetGUI v0.2")
        self.geometry("800x500")
        self.wm_attributes('-topmost', 1)
        #self.iconbitmap('favicon-20180922073644975.ico')
        self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.label.pack(side=tk.BOTTOM,fill=tk.X)
        self.label.config(text='by 张珲 有建议欢迎交流 Tel:+86 17673102113')
        #添加页面
        self.notebook = Notebook(self,height = 300,width = 600)
        self.HNJXWFrame = tk.Frame(self.notebook);self.notebook.add(self.HNJXWFrame, text="湖南经信")
        self.HNSTFrame = tk.Frame(self.notebook);self.notebook.add(self.HNSTFrame, text="湖南科技")
        self.HNFGWFrame = tk.Frame(self.notebook);self.notebook.add(self.HNFGWFrame, text="湖南发改")
        self.XTJXWFrame = tk.Frame(self.notebook);self.notebook.add(self.XTJXWFrame, text="湘潭经信")
        self.XTSTFrame = tk.Frame(self.notebook);self.notebook.add(self.XTSTFrame, text="湘潭科技")
        self.XTFGWFrame = tk.Frame(self.notebook);self.notebook.add(self.XTFGWFrame, text="湘潭发改")
        self.CSJXWFrame = tk.Frame(self.notebook);self.notebook.add(self.CSJXWFrame, text="长沙经信")
        self.CSSTFrame = tk.Frame(self.notebook);self.notebook.add(self.CSSTFrame, text="长沙科技")
        self.CSFGWFrame = tk.Frame(self.notebook);self.notebook.add(self.CSFGWFrame, text="长沙发改")
        self.notebook.pack(side=tk.LEFT, fill=tk.Y)
        #添加功能模块，搜索
        self.FunctionPart = tk.Frame(self, height=20, width=100)
        self.FunctionPart.pack(side=tk.RIGHT, fill=tk.Y)
        v = StringVar(self, value='请输入关键词进行检索')
        self.SearchList = tk.Entry(self.FunctionPart, width=20, font=('Arial', 10),textvariable=v)
        self.SearchList.pack(anchor=tk.SW,expand=tk.NO,fill=tk.X)
        self.SearchButton = tk.Button(self.FunctionPart, height=1, width=5, text="开始",command=self.Search)
        self.SearchButton.pack(anchor=tk.SW, expand=tk.NO, fill=tk.X)
        self.followStep = ''
        self.Statuslabel = tk.Label(self.FunctionPart, width=25, height=300, text="正在进行：",
                                        justify='left')
        self.Statuslabel.pack(anchor=tk.SE)
        #初始数据
        self.INIT_Data()
        self.HNJXW['outbox'], self.HNJXW['outboxflag'] = self.INIT_outbox(self.HNJXWFrame)
        self.HNST['outbox'], self.HNST['outboxflag'] = self.INIT_outbox(self.HNSTFrame)
        self.HNFGW['outbox'], self.HNFGW['outboxflag'] = self.INIT_outbox(self.HNFGWFrame)
        self.XTJXW['outbox'], self.XTJXW['outboxflag'] = self.INIT_outbox(self.XTJXWFrame)
        self.XTST['outbox'], self.XTST['outboxflag'] = self.INIT_outbox(self.XTSTFrame)
        self.XTFGW['outbox'], self.XTFGW['outboxflag'] = self.INIT_outbox(self.XTFGWFrame)
        self.CSJXW['outbox'], self.CSJXW['outboxflag'] = self.INIT_outbox(self.CSJXWFrame)
        self.CSST['outbox'], self.CSST['outboxflag'] = self.INIT_outbox(self.CSSTFrame)
        self.CSFGW['outbox'], self.CSFGW['outboxflag'] = self.INIT_outbox(self.CSFGWFrame)
        #筛选

        self.objlist = [self.HNST, self.HNFGW, self.HNJXW,
                        self.XTJXW,self.XTFGW,self.XTST,
                        self.CSJXW,self.CSFGW,self.CSST]
        self.Search()
    # 初始化各种result,
    def INIT_Data(self):
        #湖南经信、湖南发改、湖南科技
        self.hnjxw_outbox_result = []
        self.hnst_outbox_result = []
        self.hnfgw_outbox_result = []
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
        #长沙经信、发改、科技
        self.csjxw_outbox_result = []
        self.csfgw_outbox_result = []
        self.csst_outbox_result = []
        self.CSJXW = {
            'name': 'CSJXW',
            'MainURL': "http://csgy.changsha.gov.cn/XXGK/tzgg/",
            'SearchURL': "http://media.changsha.gov.cn:8088/search/search?jsoncallback=objs&sort=docreltime&order=0&siteid=115&q={}&&start={}&rows=5&_=1537778565012",
            'result': self.csjxw_outbox_result
        }
        self.CSFGW = {
            'name': 'CSFGW',
            'MainURL': "http://fgw.changsha.gov.cn/zxzx/tzgg_286/",
            'SearchURL': "http://media.changsha.gov.cn:8088/search/search?jsoncallback=objs&sort=docreltime&order=0&q={}&&start={}&rows=5&_=1537778617113",
            'result': self.csfgw_outbox_result
        }
        self.CSST = {
            'name': 'CSST',
            'MainURL': "http://kjj.changsha.gov.cn/xxgk/tzgg_27202/",
            'SearchURL': "http://media.changsha.gov.cn:8088/search/search?jsoncallback=objs&siteid=110&sort=docreltime&order=0&q={}&&start={}&rows=5&_=1537778709104",
            'result': self.csst_outbox_result
        }
        #湘潭经信、发改、科技
        self.xtjxw_outbox_result = []
        self.xtfgw_outbox_result = []
        self.xtst_outbox_result = []
        self.XTJXW = {
            'name': 'XTJXW',
            'MainURL': "http://xtst.xiangtan.gov.cn",
            'SearchURL': "http://xtjxw.xiangtan.gov.cn/fulltextsearch/rest/getfulltextdata?format=json&wd={}&sort=0&pn={}&rn=10&cl=150&idx_cgy=xtjxw",
            'result': self.xtjxw_outbox_result
        }
        self.XTFGW = {
            'name': 'XTFGW',
            'MainURL': "http://xtfgw.xiangtan.gov.cn",
            'SearchURL': "http://xtfgw.xiangtan.gov.cn/fulltextsearch/rest/getfulltextdata?format=json&wd={}&sort=0&pn={}&rn=10&cl=150&idx_cgy=xtfgw",
            'result': self.xtfgw_outbox_result
        }
        self.XTST = {
            'name': 'XTST',
            'MainURL': "http://xtst.xiangtan.gov.cn",
            'SearchURL': "http://xtst.xiangtan.gov.cn/fulltextsearch/rest/getfulltextdata?format=json&wd={}&sort=0&pn={}&rn=10&cl=150&idx_cgy=xtkjj",
            'result': self.xtst_outbox_result
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
        self.Statuslabel.config(text="正在进行.............")
        self.followStep = ''
        if keywords == "请输入关键词进行检索":
            for obj in self.objlist:
                self.followStep = self.followStep + obj['name'] + ' Done' + '\n'
                self.Statuslabel.config(text="%s" %self.followStep)
                self.initSearch(obj)
                self.Statuslabel.config(text="已完成")
        else:
            for obj in self.objlist:
                self.followStep = self.followStep + obj['name'] + ' Done' + '\n'
                self.Statuslabel.config(text="%s" % self.followStep)
                self.keywordsSearch(keywords=keywords,key=obj)
                self.Statuslabel.config(text="已完成")
        self.INIT_output()  # insert现有的result
        self.SearchButton.config(state='normal')

    # Search方法的keywords分支的实现
    def keywordsSearch(self,keywords,key):
        url = key['SearchURL']
        page = 1;endpage = 5
        res = '.*(20[0-9]{2}\-[0-9]{2}\-[0-9]{2}).*'
        if "HN" in key['name']:
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
        elif "XT" in key['name']:
            while page <= endpage:
                URL = url.format(keywords,page-1)
                response = requests.get(URL)
                result = json.loads(response.text)
                records = result['result']['records']
                for ii in records:
                    ii['title'] = str(ii['title']).replace("<font color='#CC0000'>","").replace("</font>","")
                    key['result'].append([ii['title'],ii['link'],ii['date']])
                page+=1
        elif "CS" in key['name']:
            page = 0
            while page <= endpage*4:
                URL = url.format(keywords, page)
                response = requests.get(URL)
                response = response.text.split('=')[1]
                result = json.loads(response)
                records = result['rsList']
                for ii in records:
                    T = re.match(res, ii['crtime'])[1]
                    # print(ii['doctitle'],ii['docpuburl'],T)
                    key['result'].append([ii['doctitle'],ii['docpuburl'],T])
                page+=5
    # Search方法的nullkeys分支的实现
    def initSearch(self,obj):
        url = obj['MainURL']
        pageno = 1
        endpage = 5
        if "HN" in obj['name']:
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
        elif "XT" in obj['name']:
            while pageno <= endpage:
                back = '.html'
                response = requests.get(url+'/govxxgk/001001/category/001/001007/001007002/'+str(pageno)+back)
                response.encoding = 'UTF-8'
                soup = bs(response.text, "html.parser")
                result = soup.select('div div div ul div.islinked')
                for ii in result:
                    notime = ii.select('a')[0]
                    yestime = ii.select('div.ewb-kind-time')[0].text
                    obj['result'].append([notime.text, url+notime['href'], yestime.strip()])
                pageno += 1
        elif "CS" in obj['name']:
            while pageno <= endpage:
                back = ''
                if obj['name'] == "CSST":
                    if pageno == 1:
                        back = 'index.htm'
                    else:
                        back = 'index' + '_' + str(pageno - 1) + '.htm'
                else:
                    if pageno == 1:
                        back = 'index.html'
                    else:
                        back = 'index' + '_' + str(pageno - 1) + '.html'
                response = requests.get(url + back)
                response.encoding = 'UTF-8'
                soup = bs(response.text, "html.parser")
                # 获取内容
                if obj['name'] == 'CSJXW':
                    result = soup.select('#container #main div ul li')
                    for ii in result:
                        try:
                            yestime = ii.select('span')[0]
                            notime = ii.select('a')[0]
                            obj['result'].append([notime.text,
                                                  url + notime['href'],
                                                  yestime.text.replace('[','').replace(']','')])
                        except Exception as e:
                            pass
                elif obj['name'] == 'CSFGW':
                    result = soup.select('div.page_list ul li')
                    for ii in result:
                        try:
                            yestime = ii.select('span')[0]
                            notime = ii.select('a')[0]
                            obj['result'].append([notime.text,
                                                  url + notime['href'],
                                                  yestime.text.replace('[','').replace(']','')])
                        except Exception as e:
                            pass
                elif obj['name'] == "CSST":
                    result = soup.select('div.list-box.show li')
                    for ii in result:
                        try:
                            yestime = ii.select('i')[0]
                            notime = ii.select('a')[0]
                            obj['result'].append([notime.text,
                                                  url + notime['href'],
                                                  yestime.text.replace('[','').replace(']','')])
                            # print([notime.text,
                            #                       url + notime['href'],
                            #                       yestime.text.replace('[','').replace(']','')])
                        except Exception as e:
                            pass
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
    #demo1.keywordsSearch("创新卷",demo1.CSST)
    demo1.mainloop()
