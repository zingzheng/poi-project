# -*- coding: utf-8 -*-
'''
Created on 20160807

@author: Zing
@blog: http://www.zing.ac.cn
@email: zing.ac@163.com
'''

import threading
from webserver.mybean import *
from zing import PTask

class POIAdapter(object):
    
    def __init__(self, job):
        self.job = job
        self.task = PTask.taskFac(job.takes_value())
        
    
    def run(self):
        try:
            if task.isTime():
                if task.run():
                    task.goNex()
                updata(task)    
        except Exception as e:
            updata(task)
            
    def go(self):
        try:
            t = threading.Thread(target=self.run)
            t.start()
        except Exception as e:
            updata(task)
        
    