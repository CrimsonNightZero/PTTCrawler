# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 13:22:59 2020

@author: foryou
"""

import sqlite3

# 對於資料庫操作
# db -> 資料庫
# table -> 資料表
class SQlite_Operator():
    def __init__(self, db, table):
        self.db = db
        self.table = table
        
    # 對於SQlite資料庫創建
    # 以看板名作為各資料庫的資料表
    # Tweet.db資料表格式 : id -> Primary key, authorId -> 作者編號, authorName -> 作者暱稱, 
    # title -> 標題, publishedTime -> 貼文時間, content -> 內文, canonicalUrl -> 標準網址, 
    # createdTime -> 資料建立時間, updateTime -> 資料更新時間
    # Comment.db資料表格式 : tweet_id -> 推文資料庫的id當作Foreign key, 
    # commentId -> 推文者編號, commentContent -> 推文內容, commentTime -> 推文時間
    # Log.db資料表格式 : id -> Primary key, urlIndex -> 看板Index
    def create(self):
        conn = sqlite3.connect(self.db)
    
        c = conn.cursor()
        
        if self.db == "Tweet.db":
            c.execute("CREATE TABLE " + self.table + " (id integer PRIMARY KEY AUTOINCREMENT NOT NULL, \
                      authorId text, authorName text, title text, \
                      publishedTime integer, content text, canonicalUrl text, \
                    createdTime text, updateTime text)")
       
        elif self.db == "Comment.db":
            c.execute("CREATE TABLE " + self.table + " (tweet_id integer, commentId text, \
                      commentContent text, commentTime integer)")
                
        elif self.db == "Log.db":
            c.execute("CREATE TABLE " + self.table + " (id integer PRIMARY KEY AUTOINCREMENT NOT NULL, \
                      urlIndex integer)")
        
        conn.commit()
        conn.close()
    
    # 檢查資料是否存在並回傳
    # 搜尋資料表內資料是否存在
    def check_row(self, row_filter):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        if self.db == "Tweet.db": 
            row_filter = "publishedTime ='" + row_filter[0] + "' AND canonicalUrl ='" + row_filter[1] + "'"
        
        elif self.db == "Comment.db":
            row_filter = "commentId ='" + row_filter[0] + "' AND commentContent ='" + row_filter[1].replace("'", "''") + "'"
        
        elif self.db == "Log.db":
            row_filter = "urlIndex ='" + row_filter[0] + "'"
            
        c.execute("SELECT * FROM  " + self.table + "  WHERE " + row_filter)
        
        row_exist = False
        if not c.fetchone() is None:
            row_exist = True
            
        conn.close()
        return row_exist
    
    # 檢查資料表是否存在並回傳
    def check_table(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        
        c.execute("SELECT count(name) FROM sqlite_master  WHERE type='table' AND name='" + self.table + "'")
        
        table_exits = False
        if c.fetchone()[0] == 1:
            table_exits = True
        
        conn.close()
        return table_exits
    
    # 取得推文資料庫編號
    def get_id(self, publishedTime, canonicalUrl):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        
        c.execute("SELECT id FROM " +  self.table + "  WHERE publishedTime='" + publishedTime + "' AND canonicalUrl='" + canonicalUrl + "'")
        data = c.fetchone()[0]
        conn.close()
        return data
    
    # 取得Log資料庫已搜尋過的看板藉由Index，並整理格式輸出
    def get_all_url_index(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        url_index= c.execute("SELECT urlIndex FROM " +  self.table + " ORDER BY urlIndex")
        
        urls = ""
        start = 0
        end = 0
        temp = 0
        url_index = list(url_index)
        for index, row in enumerate(url_index):
            if temp + 1 == row[0]:
                end = row[0]
                if not urls[-1] == "~":
                    urls = urls[0:-2] + "~"
            else:
                if not index == 0 and urls[-1] == "~":
                    urls += str(end) + "\n"
                start = row[0]
                urls += str(start) + "," + "\n"
            
            temp = row[0]
            
        if urls[-1] == "~":
            urls += str(temp)
        
        conn.close()
        return urls
    
    # 新增資料
    # 整理成INSERT資料格式
    # 對各資料庫新增資料
    def insert(self, datalist):
        data = self.datalist_format(datalist)
        
        conn = sqlite3.connect(self.db)

        c = conn.cursor()
        if self.db == "Tweet.db":
            col = "authorId, authorName, title, publishedTime, content, canonicalUrl, createdTime , updateTime"
            
        elif self.db == "Comment.db":
            col = "tweet_id, commentId, commentContent, commentTime"
            
        elif self.db == "Log.db":
            col = "urlIndex"
        
        c.execute("INSERT INTO  " + self.table + "(" + col + ")  VALUES (" + data +")")
        
        conn.commit()
        conn.close()
        
    # 刪除資料未使用
    # def delete(self):
    #     conn = sqlite3.connect(self.db)

    #     c = conn.cursor()
    #     sql = "DELETE FROM  " + self.table + "  WHERE id=?"
    #     c.execute(sql, (id,))
        
    #     conn.commit() 
    #     conn.close()
        
    # 整理成INSERT資料格式
    def datalist_format(self, datalist):
        data = ""
        for x in datalist:
            data += "'" + str(x).replace("'", "''") + "',"
        data = data[0:-1]
        
        return data