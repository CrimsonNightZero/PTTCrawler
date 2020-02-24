# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 16:04:20 2020

@author: foryou
"""

import re
from Module.PPTSearch import PPTSearch
from Module.SQliteOperator import SQlite_Operator
import argparse


# PPT Controller
# headers -> 標頭存取 'User-Agent': 模擬真實使用者環境, 'cookie': 通過over18頁面認證
# board_url -> 看板網址
# ppt_search -> PPTSearch Model
# ppt_search.res_time -> requests延遲時間
class PTTCrawler():
    def __init__(self, board_url, res_time):
        self.headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
           ,'cookie' : 'over18=1'}
        self.board_url = board_url
        self.ppt_search = PPTSearch(self.headers, board_url)
        self.ppt_search.res_time = res_time

    # 搜尋單一頁面
    # 搜尋看板內容並回傳連線狀態
    # 取得目前網址看板的Index
    # 對已搜尋過的看板作紀錄
    def single_search(self):
        conn_status = self.ppt_search.board_search()
        if conn_status:
            index = self.ppt_search.get_index()
            self.ppt_search.write_log(index)
            print("Check index:", index, " Connected status:", conn_status)
           
    # 搜尋指定範圍內的看板
    # 取得看板網址 
    # 搜尋看板內容並回傳連線狀態
    # 對已搜尋過的看板作紀錄 
    def range_search(self, start_index, end_index):
        for x in range(start_index, start_index + end_index + 1):
            self.board_url = self.board_url.split("index")[0] + "index" + str(x) + ".html"
            self.ppt_search.board_url = self.board_url
            conn_status = self.ppt_search.board_search()
            if conn_status:
                self.ppt_search.write_log(str(x))
                print("Check index:", x, " Connected status:", conn_status)
            
    # 從目前看板Index搜尋到最新的
    # 取得目前網址看板的Index
    # 確認連線狀態否則停止
    # 取得看板網址
    # 搜尋看板內容並回傳連線狀態
    # 對已搜尋過的看板作紀錄
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
            print("Check index:", index, " Connected status:", conn_status)
            index = int(index) + 1
            
    # 檢查看板Index
    # 取得已搜索過的看板Index，確認是否已搜尋過
    def check_board_log(self, board):
        sql = SQlite_Operator(r"Data/Log.db", board)
        print("Already search index:")
        print(sql.get_all_url_index())

# SingleSearch 搜尋單一頁面
# NewstSearch 從目前看板Index搜尋到最新的
# RangeSearch 搜尋指定範圍內的看板 : start_index -> 起始index, end_index -> 範圍
# CheckBoardLog 檢查看板Index : board -> 給定搜索的看板名
if __name__ == '__main__':
    print("Data mode : 1.SingleSearch 2.NewstSearch 3.RangeSearch 4.CheckBoardLog")

    parser = argparse.ArgumentParser(description='this script')
    parser.add_argument('--board_url', type=str, default = "https://www.ptt.cc/bbs/Gossiping/index.html")
    parser.add_argument('--run_mode', type=str, default = "1")
    parser.add_argument('--start_index', type=int, default= 30000)
    parser.add_argument('--end_index', type=int, default= 5)
    parser.add_argument('--board', type=str, default= "Gossiping")
    parser.add_argument('--res_time', type=int, default = 20)
    args = parser.parse_args()
    
    pptcrawler = PTTCrawler(args.board_url, args.res_time)
    if args.run_mode == "1" or args.run_mode == "SingleSearch":
        print("Start: SingleSearch")
        pptcrawler.single_search()
    elif args.run_mode == "2" or args.run_mode == "NewstSearch":
        print("Start: NewstSearch")
        pptcrawler.newst_search()
    elif args.run_mode == "3" or args.run_mode == "RangeSearch":
        print("Start: RangeSearch")
        pptcrawler.range_search(args.start_index, args.end_index)
    elif args.run_mode == "4" or args.run_mode == "CheckBoardLog":
        print("Start: CheckBoardLog")
        pptcrawler.check_board_log(args.board)
    print("Finish")
        