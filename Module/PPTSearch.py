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
        self.commentConten = None
        self.commentTime = 0
        self.tweet_id = 0
        self.url_index = 0
       
    def check_status(self, res):
        status = res.status_code
        
        if status == 200:
            return True
        else:
            print("Connect Error")
            return False
        
    def board_search(self):
        board_res = requests.get(self.board_url, headers = self.headers)
        
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

    def article_search(self):
        # article_url = 'https://www.ptt.cc/bbs/Gossiping/M.1582178635.A.20A.html'
        article_url = self.canonicalUrl
        article_res = requests.get(article_url, headers = self.headers)
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
        
        # 轉換為時間戳:

        for push in article_soup.select('.push'):
            if not push.select('.f3.hl.push-userid'):
                continue
            self.commentId = push.select('.f3.hl.push-userid')[0].text
            
            self.commentContent = push.select('.f3.push-content')[0].text.replace(": ", "")
            
            commentTime = push.select('.push-ipdatetime')[0].text
            if len(commentTime) == 1:
                self.commentTime = None
            else:
                mon_day = re.search("\d{2}\/\d{2}", commentTime).group(0)
                hour_min = re.search("\d{2}\:\d{2}", commentTime)
                if not hour_min:
                    hour_min = str(timeArray.tm_hour) + ":" + str(timeArray.tm_min)
                else:
                    hour_min = hour_min.group(0)
                # print(year)
                # print(not year%4==0 and not year %400==0 and year % 100==0)
                if mon_day=="02/29" and not (year%4==0 and  year %400==0 and not year % 100==0):
                    mon_day="03/01"
                    
                # print(mon_day, hour_min, year)
                commentTime =  mon_day + " " + hour_min + " " + str(year)
     
                self.commentTime, timeArray = self.get_timestamp(commentTime, "%m/%d %H:%M %Y")
            
            sql = SQlite_Operator('Tweet.db', self.board)
            self.tweet_id = sql.get_id(self.publishedTime, self.canonicalUrl)
            self.fast_insert('Comment.db', self.board)
        
    def get_timestamp(self, datatime ,time_format):
        timeArray = time.strptime(datatime, time_format)
        timestamp = str(int(time.mktime(timeArray))) + "00"
        return timestamp, timeArray
    
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
            
    def get_index(self):
        board_res = requests.get(self.board_url, headers = self.headers)
        board_soup = bs(board_res.text,"html.parser")
        page_up_url = board_soup.select('.btn.wide')[1]['href']
        index = re.search('index\d*.html', page_up_url).group(0).replace("index", "").replace(".html", "") 
        return str(int(index) + 1)
    
    def write_log(self, index):
        self.url_index = index
        self.fast_insert('Log.db', self.board)