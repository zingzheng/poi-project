# -*- coding: utf-8 -*-
'''
Created on 20160806

@author: zingzheng
@blog: http://www.zing.ac.cn
@email: zing.ac@163.com
'''

class JobInfoBean(object):
    def __init__(self):
        self.id = -1
        self.core_type =''
        self.map_type = ''
        self.region_type = ''
        self.region = ''
        self.keyword = ''
        #---
        self.delta = ''
        self.nex = ''
        self.recover = ''
        self.res = ''
        #---
        self.owner = ''
        self.createTime = ''
        self.finishTime = ''
        self.status = ''
    
    def getKeys(self):
        return ('core_type','map_type','region_type',
                'region','keyword','owner',
                'createTime','finishTime','status')
        
    def getValues(self):
        return (self.core_type,self.map_type,self.region_type,
                self.region,self.keyword,self.owner,
                self.createTime,self.finishTime,self.status)
        
    def mix(self):
        keys = self.getKeys()
        values = self.getValues()
        m = []
        for i in range(len(keys)):
            m.append(keys[i])
            m.append(values[i])
        return m
        
    def sp(self):
        return self.getKeys()+self.getValues()