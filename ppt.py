# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 16:04:20 2020

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

    def board_search(self):
        board_res = requests.get(self.board_url, headers = self.headers)
        board_soup = bs(board_res.text,"html.parser")
        
        board_soup.select('.board')[0].text.replace("看板 ","")
        for board_r_ent in board_soup.select('.r-ent'):
            self.authorId = board_r_ent.select('.author')[0].text
            if "-" == self.authorId:
                continue
            
            for board_title in board_r_ent.select('.title'):
                for board_a in board_title.select('a'):
                    self.canonicalUrl = self.url + board_a['href']
                    self.title = board_a.text
                    
                    self.article_search()
                    self.fast_insert('Tweet.db', "board")
                    self.fast_insert('Tweet.db', "board")

    def article_search(self):
        # article_url = 'https://www.ptt.cc/bbs/Gossiping/M.1580810317.A.16C.html'
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
        # 轉換為時間戳:
    
        for push in article_soup.select('.push'):
            self.commentId = push.select('.f3.hl.push-userid')[0].text
            
            self.commentContent = push.select('.f3.push-content')[0].text.replace(": ", "")
            
            commentTime = push.select('.push-ipdatetime')[0].text.split(' ')
            commentTime = commentTime[-2] + " " + commentTime[-1].strip() + " " + str(year)
            
            self.commentTime, timeArray = self.get_timestamp(commentTime, "%m/%d %H:%M %Y")
            
        localtime = time.strftime('%Y-%m-%dT%H:%M:%S.020+00:00', time.localtime())
       
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
        
        elif db == "DataUpdateTime.db":
            row_filter = [self.createdTime, self.updateTime]
        
        elif db == "Comment.db":
            row_filter = [self.commentId, self.commentContent]
            
        if not sql.check_row(row_filter):
            if db == "Tweet.db": 
                row_data = [self.authorId, self.authorName, self.title, self.publishedTime, \
                          self.content, self.canonicalUrl]
            
            elif db == "DataUpdateTime.db":
                row_data = [self.createdTime, self.updateTime]
            
            elif db == "Comment.db":
                row_data = [self.commentId, self.commentContent, self.commentTime]
            
            sql.insert(row_data)
        
if __name__ == '__main__':
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
           ,'cookie' : 'over18=1'}
    board_url = "https://www.ptt.cc/bbs/Gossiping/index38963.html"
    
    pptsearch = PPTSearch(headers, board_url)
    pptsearch.board_search()
                
       