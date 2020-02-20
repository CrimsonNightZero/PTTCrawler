# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 16:04:20 2020

@author: foryou
"""

import re
from Module.PPTSearch import PPTSearch
from Module.SQliteOperator import SQlite_Operator

class PTTCrawler():
    def __init__(self, board_url):
        self.headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
           ,'cookie' : 'over18=1'}
        self.board_url = board_url
        self.ppt_search = PPTSearch(self.headers, board_url)

    def single_search(self):
        conn_status = self.ppt_search.board_search()
        if conn_status:
            index = self.ppt_search.get_index()
            self.ppt_search.write_log(index)
            print(index, conn_status)
            
    def search_for_range(self, start_index, end_index):
        for x in range(start_index, end_index + 1):
            self.board_url = self.board_url.split("index")[0] + "index" + str(x) + ".html"
            self.ppt_search.board_url = self.board_url
            conn_status = self.ppt_search.board_search()
            if conn_status:
                self.ppt_search.write_log(str(x))
                print(x, conn_status)
            
    def newst_search(self):
        conn_status = True
        index = re.search('index\d*.html', self.board_url).group(0).replace("index", "").replace(".html", "") 
        if not index:
            index = self.ppt_search.get_index()
            
        while(conn_status):
            self.board_url = self.board_url.split("index")[0] + "index" + str(index) + ".html"
            self.ppt_search.board_url = self.board_url
            conn_status = self.ppt_search.board_search()
            if conn_status:
                self.ppt_search.write_log(str(index))
            print(index, conn_status)
            index = int(index) + 1

if __name__ == '__main__':
    board_url = "https://www.ptt.cc/bbs/Gossiping/index.html"
    # sql = SQlite_Operator("Log.db", "Gossiping")
    
    # print(sql.get_all_url_index())
    pptcrawler = PTTCrawler(board_url)
    start_index = 1
    end_index = 5
    pptcrawler.search_for_range(start_index, end_index)
    # pptcrawler.single_search()
    # pptcrawler.newst_search()
    #time process to crawler


       