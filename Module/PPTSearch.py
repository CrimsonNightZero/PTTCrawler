# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 12:59:36 2020

@author: foryou
"""

import requests
from bs4 import BeautifulSoup as bs
import re 
import time
from Module.SQliteOperator import SQlite_Operator

# authorId aby123
# authorName 批踢踢小新手
# title 到底為啥要隱瞞實情啊
# publishedTime 1580810315000
# content 完整內文
# canonicalUrl https://www.ptt.cc/bbs/Gossiping/M.1580810317.A.16C.html
# createdTime 2019-12-13T18:37:22.020+00:00
# updateTime 2019-12-13T18:37:22.020+00:00
# commentId elec1141
# commentContent 完整推文
# commentTime 1580820642000

# PPT網頁搜索
# headers -> 標頭存取
# url -> 根部網址
# board_url -> 看板網址
# board -> 看版名
# authorId -> 作者編號
# authorName -> 作者暱稱
# title -> 標題
# publishedTime -> 貼文時間
# content -> 內文
# canonicalUrl -> 標準網址
# createdTime -> 資料建立時間
# updateTime -> 資料更新時間
# commentId -> 推文者編號
# commentContent -> 推文內容
# commentTime -> 推文時間
# tweet_id -> 推文資料庫的id
# url_index -> 看板Index
# res_time -> requests延遲時間
class PPTSearch():
    def __init__(self, headers, board_url):
        self.headers = headers 
        self.url = "https://www.ptt.cc"
        self.board_url = board_url
        self.board = None
        self.authorId = None
        self.authorName = None
        self.title = None
        self.publishedTime = 0
        self.content = ""
        self.canonicalUrl = None
        self.createdTime = None
        self.updateTime = None
        self.commentId = None
        self.commentContent = None
        self.commentTime = 0
        self.tweet_id = 0
        self.url_index = 0
        self.res_time = 0
    
    # 對requests設定延遲避免對網站操作太頻繁
    def redefine_res(self, url):
        time.sleep(self.res_time)
        res = requests.get(url, headers = self.headers)
        return res
    
    #檢查requests後網站的狀態
    def check_status(self, res):
        status = res.status_code
        
        if status == 200:
            return True
        else:
            print("Connect Error")
            return False
        
    # 取得看版網站html的內容並解析其內容
    # 取得此頁看板名、作者編號、文章標準網址、文章標題
    # 搜尋此頁看板內所有文章
    def board_search(self):
        board_res = self.redefine_res(self.board_url)
        
        if not self.check_status(board_res):
            return False
        
        board_soup = bs(board_res.text,"html.parser")
        
        self.board = board_soup.select('.board')[0].text.replace("看板 ","")
        for board_r_ent in board_soup.select('.r-ent'):
            self.authorId = board_r_ent.select('.author')[0].text
            if "-" == self.authorId:
                continue
            
            for board_title in board_r_ent.select('.title'):
                for board_a in board_title.select('a'):
                    self.canonicalUrl = self.url + board_a['href']
                    self.title = board_a.text
                    
                    self.article_search()
                    
        return True
    
    # 取得文章網站html的內容並解析其內容
    # 取得作者暱稱、內文
    # 取得貼文時間、資料建立時間、資料更新時間並轉換成時間戳
    # 存取推文資料庫
    # 取得推文者編號、推文內容
    # 取得推文時間，文章與回覆同月同日時不顯示時，藉由貼文時間取得月日、
    # 解決最開始的文章有閏年問題導致時間戳無法轉換
    # 取得推文資料庫編號對資料庫對應
    # 存取推文資料庫
    def article_search(self):
        # article_url = 'https://www.ptt.cc/bbs/Gossiping/M.1582178635.A.20A.html'
        article_url = self.canonicalUrl
        article_res = self.redefine_res(article_url)
        article_soup = bs(article_res.text,"html.parser")
        authorName = article_soup.select('.article-metaline')[0].text
        
        authorName = re.search('\(.*\)', authorName).group(0)
        self.authorName = authorName.replace('(', "").replace(')', "")
        
        publishedTime = article_soup.select('.article-metaline')[2].text.replace("時間","")
    
        main_content = article_soup.select('#main-content')[0].text
        self.content = ""
        for i, content in enumerate(main_content.split('\n')):
            if i == 0:
                continue
            elif '※ 發信站: 批踢踢實業坊(ptt.cc)' in content:
                break
            self.content += content + "\n"
        
        self.publishedTime, timeArray = self.get_timestamp(publishedTime,"%a %b %d %H:%M:%S %Y")
        year = timeArray.tm_year
        
        localtime = time.strftime('%Y-%m-%dT%H:%M:%S.020+00:00', time.localtime())
        
        self.createdTime = localtime
        self.updateTime = localtime
        
        self.fast_insert('Tweet.db', self.board)
        
        for push in article_soup.select('.push'):
            if not push.select('.f3.hl.push-userid'):
                continue
            self.commentId = push.select('.f3.hl.push-userid')[0].text
            
            self.commentContent = push.select('.f3.push-content')[0].text.replace(": ", "")
            
            commentTime = push.select('.push-ipdatetime')[0].text
            if len(commentTime) == 1:
                self.commentTime = None
            else:
                mon_day = re.search("\d{2}\/\d{2}", commentTime)
                hour_min = re.search("\d{2}\:\d{2}", commentTime)
                if not hour_min:
                    hour_min = str(timeArray.tm_hour) + ":" + str(timeArray.tm_min)
                else:
                    hour_min = hour_min.group(0)
                    
                if not mon_day:
                    mon_day = str(timeArray.tm_mon) + "/" + str(timeArray.tm_mday)
                else:
                    mon_day = mon_day.group(0)
               
                if mon_day=="02/29" and not (year%4==0 and  year %400==0 and not year % 100==0):
                    mon_day="03/01"
                    
                commentTime =  mon_day + " " + hour_min + " " + str(year)
     
                self.commentTime, timeArray = self.get_timestamp(commentTime, "%m/%d %H:%M %Y")
            
            sql = SQlite_Operator('Tweet.db', self.board)
            self.tweet_id = sql.get_id(self.publishedTime, self.canonicalUrl)
            self.fast_insert('Comment.db', self.board)
            
    # 轉換時間戳並修正格式
    def get_timestamp(self, datatime ,time_format):
        timeArray = time.strptime(datatime, time_format)
        timestamp = str(int(time.mktime(timeArray))) + "00"
        return timestamp, timeArray
    
    # 快速存取資料庫
    # 檢查資料表是否存在，不存在則創建新的
    # 以publishedTime, canonicalUrl辨別資料重複性
    # commentId, commentContent辨別資料重複性
    # url_index辨別資料重複性
    # 檢查資料是否存在，沒有重複則新增資料
    def fast_insert(self, db, table):
        sql = SQlite_Operator(db, table)
        if not sql.check_table():
            sql.create()
        
        if db == "Tweet.db": 
            row_filter = [self.publishedTime, self.canonicalUrl]
            row_data = [self.authorId, self.authorName, self.title, self.publishedTime, \
                          self.content, self.canonicalUrl, self.createdTime, self.updateTime]
        
        elif db == "Comment.db":
            row_filter = [self.commentId, self.commentContent]
            row_data = [self.tweet_id, self.commentId, self.commentContent, self.commentTime]

        elif db == "Log.db":
            row_filter = [self.url_index]
            row_data = [self.url_index]
            
        if not sql.check_row(row_filter):
            sql.insert(row_data)
    
    # 當目前看版沒有編號時透過上頁取得目前看版編號
    def get_index(self):
        board_res = self.redefine_res(self.board_url)
        board_soup = bs(board_res.text,"html.parser")
        page_up_url = board_soup.select('.btn.wide')[1]['href']
        index = re.search('index\d*.html', page_up_url).group(0).replace("index", "").replace(".html", "") 
        return str(int(index) + 1)
    
    # 存取日誌資料庫
    def write_log(self, index):
        self.url_index = index
        self.fast_insert('Log.db', self.board)