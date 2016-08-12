# -*- coding: utf-8 -*-
'''
Created on 20160806

@author: zingzheng
@blog: http://www.zing.ac.cn
@email: zing.ac@163.com
'''

class JobInfoBean(object):
    def __init__(self):
        self.id = 0
        #---
        self.core_type ='1'
        self.map_type = '2'
        self.region_type = '3'
        self.region = '4'
        self.keyword = '5'
        self.delta = '6'
        self.nex = '7'
        self.boxs = '8'
        self.res = '9'
        self.log = '10'
        #---
        self.owner = '11'
        self.createTime = '12'
        self.finishTime = '13'
        self.status = '14'
    
    def getKeys(self):
        return ('core_type','map_type','region_type',
                'region','keyword','owner',
                'delta','nex','boxs','res','log',
                'createTime','finishTime','status')
        
    def getValues(self):
        return (self.core_type,self.map_type,self.region_type,
                self.region,self.keyword,self.owner,
                self.delta,self.nex,self.boxs,self.res,self.log,
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