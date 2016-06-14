# -*- coding: utf-8 -*-
'''
Created on 2016年6月14日

@author: zingzheng
'''

'''
地图方言的基类
'''
class BaseMap(object):
    
    def __init__(self):
        pass
    
    def conUrl(self):
        pass
    
    def request(self):
        pass
    
    def getRes(self):
        self.request()
        pass
    
    def getSub(self):
        pass
    
    def parser(self):
        pass
    
'''
具体的地图类：百度地图
'''   
class BaiduMap(BaseMap):
    
    def __init__(self):
        pass