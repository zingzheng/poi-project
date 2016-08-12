# -*- coding: utf-8 -*-
'''
Created on 20160807

@author: Zing
@blog: http://www.zing.ac.cn
@email: zing.ac@163.com
'''

import threading
from webserver.mybean import *
from webserver.mydao import *
from zing import PTask
import datetime

class POIAdapter(object):
    
    def __init__(self, job):
        self.job = job
        self.task = self.jobToTask(job)

    def jobToTask(self,job):
        args = [job.core_type,job.map_type,job.region_type,job.region,job.keyword,
                job.delta,job.nex]
        if job.boxs:
            args.append(job.boxs)
            args.append(job.res)
        return PTask.taskFac(args)
    
    def updateJob(self):
        self.job.nex = self.task.nex
        self.job.boxs = self.task.boxsPath
        self.job.res = self.task.filePath
        self.job.log = self.task.logPath
        self.job.finishTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.job.boxs:
            self.job.status = 'fail'
        else:
            self.job.status = 'success'
        JobInfoDao().update(self.job)
        
    
    def run(self):
        try:
            if self.task.isTime():
                if self.task.run():
                    self.task.goNex()
                self.updateJob()    
        except Exception as e:
            self.updateJob()
            
    def go(self):
        t = threading.Thread(target=self.run)
        t.start()
        
    