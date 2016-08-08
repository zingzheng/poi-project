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

class POIAdapter(object):
    
    def __init__(self, job):
        self.job = job
        self.task = self.jobToTask(job)
        self.jobDao = JobInfoDao()
    
    @staticmethod
    def jobToTask(job):
        args = [job.core_type,job.map_type,job.region_type,job.region,job.keyword,job.delta,
                job.nex]
        if job.recover:
            args.append(job.recover)
            args.append(job.res)
        PTask.taskFac(args)
    
    def taskToJob(self):
        self.job.nex = self.task.nex
        self.job.res = self.task.res
        if self.task.recover:
            self.job.recover = self.task.recover
            self.job.state = 'fail'
        else:
            self.job.state = 'success'
    
    def run(self):
        try:
            if self.task.isTime():
                if self.task.run():
                    self.task.goNex()
                self.taskToJob()
                self.jobDao.update(self.job)    
        except Exception as e:
            self.taskToJob()
            self.jobDao.update(self.job)
            
    def go(self):
        t = threading.Thread(target=self.run)
        t.start()
        self.jobDao.update(self.job)
        
    