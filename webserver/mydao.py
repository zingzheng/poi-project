# -*- coding: utf-8 -*-
'''
Created on 20160806

@author: zingzheng
@blog: http://www.zing.ac.cn
@email: zing.ac@163.com
'''
from contextlib import closing
import sqlite3
import os

class BaseDao(object):

    def connect_db(self):
        return sqlite3.connect(self.mydb)
    

    def init_db(self):
        print('init db ' + self.mydb)
        if os.path.exists(self.mydb):
            return
        with closing(self.connect_db()) as db:
            with open(self.sqlSchema, 'r') as f:
                db.cursor().executescript(f.read())
            db.commit()

 
class JobInfoDao(BaseDao):
    def __init__(self):
        self.BASEPATH = os.path.split(os.path.realpath(__file__))[0]
        self.sqlSchema = self.BASEPATH+'/db/JobInfo-schema.sql'
        self.mydb = self.BASEPATH+'/db/JobInfo.sql'
        
    def insert(self,job):
        with closing(JobInfoDao().connect_db()) as db:
            db.cursor().execute("insert into JobInfo(%s,%s,%s,%s,%s,%s,%s,%s,%s)\
                values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % job.sp())
            db.commit()
            
    def select(self):
        rows = None
        with closing(JobInfoDao().connect_db()) as db:
            cursor = db.cursor()
            cursor.execute('select * from JobInfo')
            rows = cursor.fetchall()
            cursor.close()
        return rows
    

def init_all_db():
    j = JobInfoDao()
    j.init_db()
    
    
if __name__ == '__main__':
    init_all_db()
     
                
