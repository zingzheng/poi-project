# -*- coding: utf-8 -*-
'''
Created on 2016年6月14日

@author: zingzheng
'''

import os
import json
import time.sleep as sleep
from urllib.parse import urlencode
from urllib import request

import logging

BASE_PATH = os.path.split(os.path.realpath(__file__))[0]
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=BASE_PATH+'/log.txt',
                filemode='a')
console = logging.StreamHandler()  
console.setLevel(logging.INFO)   
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')  
console.setFormatter(formatter)  
logging.getLogger('').addHandler(console) 

class POI(object):
    '''
    poi信息bean类
    '''
    
    name = 'na'
    stree_num = 'na'
    lat = 'na'
    lng = 'na'
    address = 'na'
    adcode = 'na'
    country = 'na'
    province = 'na'
    city = 'na'
    district='na'
    stree='na'
    
    def toString(self):
        try:
            ','.join([str(s) for s in [
                    self.name, self.stree_num, self.lat, self.lng,
                    self.address, self.adcode, self.country,
                    self.province, self.city, self.district, self.stree]])
        except Exception as e:
            logging.ERROR("error in str poi")
            logging.ERROR(e)
            
        

class BaseMap(object):
    '''
    地图方言的基类
    目前支持的方言子类包括：百度、腾讯、高德
    '''
    
    def __init__(self):
        pass
    
    #根据不同的切分内核创建不同的请求URL
    def conSearchUrl(self, keyword, region, index):
        if type(region) == type("aaa"):
            return self._conSubUrl(self, keyword, region, index)
        else:
            return self._conBoxUrl(self, keyword, region, index)
    
    
    def _conSubUrl(self, keyword, region, index):
        pass
    
    
    def _conBoxUrl(self, keyword, region, index):
        pass  
    
    #构建逆地址查询url
    def _conReUrl(self, location):
        pass
    
    #发送get请求，若连接失败，自动重试re次。若失败，返回None
    def request(self, url):
        re = 3
        res = None
        while re:
            re-=1
            try:
                f = request.urlopen(url)
                res = json.loads(f.read().decode('utf-8'))
            except Exception as e:
                logging.error("erro while conn: %s" %(url))
                logging.error(e)
                sleep(0.2)
                continue
        return res
    
    #获取请求结果 statue(True,False)，message
    def getStatue(self, res):
        pass
    
    #返回结果条数，0：无,n：n,-1：溢出
    def getCount(self, res):
        pass
    
    
    #均采用高德的行政区域划分
    def getSub(self):
        pass
    
    #将搜索结果转化为需求的数据
    def parser(self,res):
        pass
            
                
        


'''
具体的地图类：百度地图
'''   
class BaiduMap(BaseMap):
    
    def __init__(self):
        self.KEY = 'voRyF7opZzGGETYert5D2PYk'
        self.SEARCH_URL = 'http://api.map.baidu.com/place/v2/search?'
        self.REGEO_URL = 'http://api.map.baidu.com/geocoder/v2/?'
        self.size = 50
    
    #location = [lat,lng]    
    def _conReUrl(self, location):
        REGEO_PARA = {
            'ak':self.KEY,
            'location':'lat,lng',
            'output':'json'
            }
        REGEO_PARA['location'] = '%f,%f'%(location)
        
        
    def _conSubUrl(self, keyword, region, index):
        pass
    
    #region = [左下lng,左下lat,右上lng,右上lat]
    def _conBoxUrl(self, keyword, region, index):
        SEARCH_PARA = {
            'ak':self.KEY,
            'bounds':'左下lat,左下lng,右上lat,右上lng',
            'q':'学校',
            'page_size':'20',
            'page_num':'0',
            'output':'json'
            }
        SEARCH_PARA['q'] = keyword
        #百度的起始页是0
        SEARCH_PARA['page_num'] = index-1
        SEARCH_PARA['bounds'] = '%f,%f,%f,%f'%(region[1],region[0],region[3],region[2])
        url = self.SEARCH_URL + urlencode(SEARCH_PARA)
        return url
    
    def getCount(self, res):
        count = int(res['total'])
        if count >= 400:
            count = -1
        return count
    
    def getStatue(self, res):
        if res == None:
            return False,"conn error"
        if int(res['status']) != 0:
            return False,res['message']
        return True,'ok'
    
    def parser(self, res):
        pois = [] 
        datas = res['result']
        if len(datas) == 0:
            return None
    
        for data in datas:
            try:
                poi = POI()
                poi.name = data['name']
                poi.lat = data['location']['lat']
                poi.lng = data['location']['lng'] 
                
                rURL = self.conReUrl([poi.lat, poi.lng])
                rRes = self.request(rURL)
                stat,msg = self.getStatue(rRes)
                if not stat:
                    logging.WARN("failed request: %s,%s"%(rURL, msg))
                    continue
                regeo = rRes['result']
                poi.stree_num = regeo['addressComponent']['street_number']
                poi.address = regeo['formatted_address']
                poi.adcode = regeo['addressComponent']['adcode']
                poi.country = regeo['addressComponent']['country']
                poi.province = regeo['addressComponent']['province']
                poi.city = regeo['addressComponent']['city']
                poi.district = regeo['addressComponent']['district']
                poi.stree = regeo['addressComponent']['street'] 
                pois.append(poi)       
            except Exception as e:
                logging.ERROR("error while parse data")
                logging.ERROR(e)
                continue
        return pois
    
def map_fac(mapType):
    if mapType == '百度':
        return BaiduMap()