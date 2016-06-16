# -*- coding: utf-8 -*-
'''
Created on 2016年6月14日

@author: zingzheng
'''

import os
import json
from time import sleep
from urllib.parse import urlencode
from urllib import request

from zing.Util import logging

BASE_PATH = os.path.split(os.path.realpath(__file__))[0]

class POI(object):
    '''
    #poi信息bean类
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
        poistr = None
        try:
            poistr = ','.join([str(s) for s in [
                    self.name, self.stree_num, self.lat, self.lng,
                    self.address, self.adcode, self.country,
                    self.province, self.city, self.district, self.stree]])
        except Exception as e:
            logging.error("error in str poi")
            logging.error(e)
        return poistr
        

class BaseMap(object):
    '''
    #地图方言的基类
    #目前支持的方言子类包括：百度、腾讯、高德
    '''
    
    def __init__(self):
        pass
    
    
    def conSearchUrl(self, keyword, region, index):
        '''
        #根据不同的切分内核创建不同的请求URL
        '''
        if type(region) == type("aaa"):
            return self._conRegUrl(keyword, region, index)
        else:
            return self._conBoxUrl(keyword, region, index)
    
    
    def _conRegUrl(self, keyword, region, index):
        '''
        #构建按行政区域搜索查询url,抽象方法
        '''
        pass
    
    
    def _conBoxUrl(self, keyword, region, index):
        '''
        #构建按矩形区域搜索查询url,抽象方法
        '''
        pass  
    
    
    def _conReUrl(self, location):
        '''
        #构建逆地址查询url,抽象方法
        '''
        pass
    
    
    def request(self, url):
        '''
        #发送get请求，若连接失败，自动重试re次。若失败，返回None
        '''
        re = 3
        res = None
        sleep(1)
        while re:
            re-=1
            try:
                f = request.urlopen(url, timeout=5)
                res = json.loads(f.read().decode('utf-8'))
            except Exception as e:
                logging.error("erro while conn: %s" %(url))
                logging.error(e)
                continue
        return res
    
    
    def getStatue(self, res):
        '''
        #获取请求结果 statue(True,False)，message。抽象方法。
        '''
        pass
    
   
    def getCount(self, res):
        '''
        #返回结果条数，0：无,n：n,-1：溢出。抽象方法。
        '''
        pass
    
    
    
    def getSub(self):
        '''
        #实时行政区域划分
        '''
        pass
    
    
    def parser(self,res):
        '''
        #将搜索结果转化为需求的数据。抽象方法。
        '''
        pass
            

class TencentMap(BaseMap):
    '''
    #具体的地图类：腾讯地图
    '''                
    
    def __init__(self):
        self.KEY = '56SBZ-VEPWV-HSDPF-US3FK-HH4G6-JPFQ7'
        self.SEARCH_URL = 'http://apis.map.qq.com/ws/place/v1/search?'
        self.REGEO_URL = 'http://apis.map.qq.com/ws/geocoder/v1/?'
        self.size = 20
        
    def _conReUrl(self, location):
        '''
        #逆地址解析URL
        #location = [lat,lng]
        '''
        REGEO_PARA = {
            'key':self.KEY,
            'location':'lat,lng'
            }
        REGEO_PARA['location'] = '%f,%f'%location
        url = self.REGEO_URL + urlencode(REGEO_PARA)
        return url
    
    def _conRegUrl(self, keyword, region, index):
        '''
        #构建按照行政区域搜索的URL
        '''
        SEARCH_PARA = {
            'boundary':'region('+region+',0)',
            'page_size':self.size,
            'page_index':index,
            'keyword':keyword,
            'key':self.KEY
            }
        url = self.SEARCH_URL + urlencode(SEARCH_PARA)
        return url
    
    def _conBoxUrl(self, keyword, region, index):
        '''
        #构建按照矩形区域搜索的URL
        #region = [左下lng,左下lat,右上lng,右上lat]
        '''
        pass
    
    def getSub(self,region):
        '''
        #获取实时行政子区域
        '''
        url = 'http://apis.map.qq.com/ws/district/v1/getchildren?&id=%s&key=%s' % (region, self.KEY)
        res = self.request(url)
        stat,msg = self.getStatue(res)
        if not stat:
            logging.error("获取行政子区域失败 %s,%s"%(msg,url))
            return None
        sub = []
        for d in res['result'][0]:
            sub.append(d['id'])
        return sub
    
    def getCount(self, res):
        '''
        #返回结果条数，0：无,n：n,-1：溢出。
        '''
        if not res:
            return 0
        count = int(res['count'])
        if 0<count<2200:
            return count
        if count >= 2200:
            return -1
        try:
            res['cluster']
            return -1
        except:
            return 0
    
    
    def getStatue(self, res):
        '''
        #解析结果的状态
        '''
        if res == None:
            return False,"conn error"
        if int(res['status']) != 0:
            return False,res['message']
        return True,'ok'    

    def parser(self, res):
        pois = [] 
        datas = res['data']
        if len(datas) == 0:
            return None
    
        for data in datas:
            try:
                poi = POI()
                poi.name = data['title']
                poi.lat = float(data['location']['lat'])
                poi.lng = float(data['location']['lng'])
                rURL = self._conReUrl((poi.lat, poi.lng))
                rRes = self.request(rURL)
                stat,msg = self.getStatue(rRes)
                if not stat:
                    logging.warn("failed request: %s,%s"%(rURL, msg))
                    continue
                regeo = rRes['result']
                poi.stree_num = regeo['address_component']['street_number']
                poi.address = regeo['address']
                poi.adcode = regeo['ad_info']['adcode']
                poi.country = regeo['address_component']['nation']
                poi.province = regeo['address_component']['province']
                poi.city = regeo['address_component']['city']
                poi.district = regeo['address_component']['district']
                poi.stree = regeo['address_component']['street']
                pois.append(poi)       
            except Exception as e:
                logging.error("error while parse data")
                logging.error(e)
                continue
        return pois
    
#--------------------------------
        
  
class BaiduMap(BaseMap):
    
    '''
    #具体的地图类：百度地图
    ''' 
    
    def __init__(self):
        self.KEY = 'voRyF7opZzGGETYert5D2PYk'
        self.SEARCH_URL = 'http://api.map.baidu.com/place/v2/search?'
        self.REGEO_URL = 'http://api.map.baidu.com/geocoder/v2/?'
        self.size = 20
    
        
    def _conReUrl(self, location):
        '''
        #逆地址解析URL
        #location = [lat,lng]
        '''
        REGEO_PARA = {
            'ak':self.KEY,
            'location':'lat,lng',
            'output':'json'
            }
        REGEO_PARA['location'] = '%f,%f'%location
        url = self.REGEO_URL + urlencode(REGEO_PARA)
        return url
        
        
    def _conRegUrl(self, keyword, region, index):
        pass
    
    
    def _conBoxUrl(self, keyword, region, index):
        '''
        #构建按照矩形区域搜索的URL
        #region = [左下lng,左下lat,右上lng,右上lat]
        '''
        SEARCH_PARA = {
            'ak':self.KEY,
            'bounds':'左下lat,左下lng,右上lat,右上lng',
            'q':'学校',
            'page_size':self.size,
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
        '''
        #返回结果条数，0：无,n：n,-1：溢出。
        '''
        if not res:
            return 0
        count = int(res['total'])
        if count >= 400:
            count = -1
        return count
    
    def getStatue(self, res):
        '''
        #解析结果的状态
        '''
        if res == None:
            return False,"conn error"
        if int(res['status']) != 0:
            return False,res['message']
        return True,'ok'
    
    def parser(self, res):
        pois = [] 
        datas = res['results']
        if len(datas) == 0:
            return None
    
        for data in datas:
            try:
                poi = POI()
                poi.name = data['name']
                poi.lat = float(data['location']['lat'])
                poi.lng = float(data['location']['lng'])
                
                rURL = self._conReUrl((poi.lat, poi.lng))
                rRes = self.request(rURL)
                stat,msg = self.getStatue(rRes)
                if not stat:
                    print(rURL,msg)
                    logging.warn("failed request: %s" % (msg))
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
                logging.error("error while parse data")
                logging.error(e)
                continue
        return pois

    
def map_fac(mapType):
    '''
    #地图方言工厂方法
    '''
    if mapType == '百度':
        return BaiduMap()
    elif mapType == '腾讯':
        return TencentMap()