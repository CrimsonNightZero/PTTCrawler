# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 13:22:59 2020

@author: foryou
"""

import sqlite3

class SQlite_Operator():
    def __init__(self, db, table):
        self.db = db
        self.table = table
        
        # datatime
        # board_id
    def create(self):
        conn = sqlite3.connect(self.db)
    
        c = conn.cursor()
        
        if self.db == "Tweet.db":
            c.execute("CREATE TABLE " + self.table + " (id integer PRIMARY KEY AUTOINCREMENT NOT NULL, \
                      authorId text, authorName text, title text, \
                      publishedTime integer, content text, canonicalUrl text)")
        
        elif self.db == "DataUpdateTime.db":
            c.execute("CREATE TABLE " + self.table + " (id integer, createdTime text, \
                      updateTime text)")
       
        elif self.db == "Comment.db":
            c.execute("CREATE TABLE " + self.table + " (id integer, commentId text, \
                      commentContent text, commentTime integer)")
        
        conn.commit()
        conn.close()
        
    def check_row(self, row_filter):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        if self.db == "Tweet.db": 
            row_filter = "publishedTime ='" + row_filter[0] + "' AND canonicalUrl ='" + row_filter[1] + "'"
        
        elif self.db == "DataUpdateTime.db":
            row_filter = "createdTime ='" + row_filter[0] + "' AND updateTime ='" + row_filter[1] + "'"
        
        elif self.db == "Comment.db":
            row_filter = "commentId ='" + row_filter[0] + "' AND commentContent ='" + row_filter[1] + "'"
    
        c.execute("SELECT * FROM  " + self.table + "  WHERE " + row_filter)
        
        row_exist = False
        if not c.fetchone() is None:
            row_exist = True
            
        conn.close()
        return row_exist
    
    def check_table(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        
        c.execute("SELECT count(name) FROM sqlite_master  WHERE type='table' AND name='" + self.table + "'")
        table_exits = False
        if c.fetchone()[0] == 1:
            table_exits = True
        # for row in c.execute("SELECT * FROM  " + self.table + "  ORDER BY id"):
            # print(row)
        
        conn.close()
        return table_exits
        
    def insert(self, datalist):
        data = self.datalist_format(datalist)
        
        conn = sqlite3.connect(self.db)

        c = conn.cursor()
        
        c.execute("INSERT INTO  " + self.table + "(authorId, authorName, title, \
                  publishedTime, content, canonicalUrl)  VALUES (" + data +")")
        
        conn.commit()
        conn.close()
        
    def delete(self):
        conn = sqlite3.connect(self.db)

        c = conn.cursor()
        sql = "DELETE FROM  " + self.table + "  WHERE id=?"
        c.execute(sql, (id,))
        
        conn.commit() 
        conn.close()
        
    def datalist_format(self, datalist):
        data = ""
        for x in datalist:
            data += "'" + x + "',"
        data = data[0:-1]
        
        return data