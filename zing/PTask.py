# -*- coding: utf-8 -*-
'''
Created on 2016年6月14日

@author: zingzheng
'''

import datetime

'''
任务的基类
'''
class BaseTask(object):
    
    def __init__(self,args):
        self.map_type = args[0]
        self.region_type = args[1]
        self.region = args[2]
        self.keyword = args[3]
        self.delat = args[4]
        if len(args) == 6:
            self.nex = self.up_to_now(args[4])
        else:
            self.nex = self.time_to_str(datetime.datetime.now())
    
    
    #字符串格式日期转datetime    
    def str_to_time(self, s):
        return datetime.datetime.strptime(s, '%Y%m%d')

    #datetime格式日期转字符串
    def time_to_str(self, t):
        return t.strftime('%Y%m%d')  

    ##若时间已经过时，自动更新到当前
    def up_to_now(self, s_nex):
        now = datetime.datetime.now()
        nex = self.str_to_time(s_nex)
        if (now-nex).days > 0:
            return self.time_to_str(now)
        else:
            return s_nex

    ##更新下次执行时间
    def goNex(self):
        self.nex = self.time_to_str(self.str_to_time(self.nex) + datetime.timedelta(days=int(self.delta)))
    
    ##判断当前任务是否需要被执行
    def isTime(self):
        now = datetime.datetime.now()
        nex = self.str_to_time(self.nex)
        if (now-nex).days >= 0:
            return True
        else:
            return False
    
    def toList(self):
        return [self.map_type,self.region_type, self.region, self.keyword, self.delta, self.nex]

    def toStr(self):
        return ' '.join(self.toList())


    
    
'''
以行政区域划分的任务类
'''
class SubTask(BaseTask):
    
    def __int__(self):
        pass
    
'''
以网格划分的任务类
'''
class CutTask(BaseTask):
    
    def _init__(self,args):
        super(args)
        