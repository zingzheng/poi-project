# -*- coding: utf-8 -*-
'''
Created on 2016年6月14日

@author: zingzheng
@blog: http://www.zing.ac.cn
@email: zing.ac@163.com
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
    
#------

class GaodeMap(BaseMap):
    '''
    #具体的地图类：高德地图
    #高德api只支持1000次每天，肯定有问题
    '''
    
    def __init__(self):
        self.KEY = 'd74aa1ef25769557ba86c90c7a953337'
        #self.KEY = '42418aff604a1c1ac2368abece1d97ba'
        #self.KEY = '40c824f549f1a5e019e108725766a019'
        #self.KEY = '3bf16b36729b31f7e985b55793f3a821'
        self.SEARCH_URL = 'http://restapi.amap.com/v3/place/text?'
        self.REGEO_URL = ' http://restapi.amap.com/v3/geocode/regeo?'
        self.size = 50
        
    def _conReUrl(self, location):
        '''
        #高德：逆地址解析URL
        #location = [lat,lng]
        '''
        REGEO_PARA = {
            'key':self.KEY,
            'location':'lng,lat'
            }
        REGEO_PARA['location'] = '%f,%f'%(location[1],location[0])
        url = self.REGEO_URL + urlencode(REGEO_PARA)
        return url
    
    def _conRegUrl(self, keyword, region, index):
        '''
        #高德：构建按照行政区域搜索的URL
        '''
        SEARCH_PARA = {
            'city':region,
            'citylimit':'true',
            'offset':self.size,
            'page':index,
            'keywords':keyword,
            'key':self.KEY,
            'children':'0'
            }
        url = self.SEARCH_URL + urlencode(SEARCH_PARA)
        return url
    
    def _conBoxUrl(self, keyword, region, index):
        '''
        #高德：构建按照矩形区域搜索的URL（只支持1000次每天，box划分肯定超过限制）
        #region = [左下lng,左下lat,右上lng,右上lat]
        '''
        pURL = ' http://restapi.amap.com/v3/place/polygon?'
        SEARCH_PARA = {
            'key':self.KEY,
            'polygon':'左上lng,左上lat;右下lng,右下lat' ,
            'keywords':keyword,
            'offset':self.size,
            'page':index,
            }
        SEARCH_PARA['polygon'] = '%f,%f;%f,%f'%(region[0],region[3],region[2],region[1])
        url = pURL + urlencode(SEARCH_PARA)
        return url
    
    def getSub(self,region):
        '''
        #高德：获取实时行政子区域（用的是腾讯的）
        '''
        key = 'JAGBZ-IQU3X-YJR4A-7S64I-HSZHK-6QBDI'
        #腾讯没有对中国进行编码，需要做特殊处理
        if int(region) == 100000:
            url = 'http://apis.map.qq.com/ws/district/v1/list?key='+key
        else:
            url = 'http://apis.map.qq.com/ws/district/v1/getchildren?&id=%s&key=%s' % (region, key)
        res = self.request(url)
        #状态获取应也用腾讯的
        stat,msg = TencentMap.getStatue(self,res)
        if not stat:
            logging.error("获取行政子区域失败 %s,%s"%(msg,url))
            return None
        sub = []
        for d in res['result'][0]:
            sub.append(d['id'])
        return sub
    
    def getCount(self, res):
        '''
        #高德：返回结果条数，0：无,n：n,-1：溢出。
        '''
        if not res:
            return 0
        count = int(res['count'])
        if 0<count<1000:
            return count
        #高德溢出和没有的返回是一样的，在行政区域划分应该没有问题
        #但是在网格划分可能会存在问题
        return -1
    
    def getStatue(self, res):
        '''
        #高德：解析结果的状态
        '''
        if res == None:
            return False,"conn error"
        if int(res['status']) != 1:
            return False,res['infocode']
        return True,'ok'    
    
    def parser(self, res):
        '''
        #高德：解析结果，并做逆地址解析
        '''
        pois = [] 
        datas = res['pois']
        if len(datas) == 0:
            return None
    
        for i in range(len(datas)):
            data = datas[i]
            try:
                poi = POI()
                poi.name = data['name']
                poi.lng,poi.lat = data['location'].split(',')
                rURL = self._conReUrl((float(poi.lat), float(poi.lng)))
                rRes = self.request(rURL)
                stat,msg = self.getStatue(rRes)
                if not stat:
                    logging.error("failed request: %s,%s"%(msg,rURL))
                    return False
                regeo = rRes['regeocode']
                try:
                    poi.stree_num = regeo["streetNumber"]['street']
                except:
                    poi.stree_num = ''
                poi.address = regeo['formatted_address']
                poi.adcode = regeo['addressComponent']['adcode']
                poi.country = regeo['addressComponent']['country']
                poi.province = regeo['addressComponent']['province']
                poi.city = regeo['addressComponent']['city']
                poi.district = regeo['addressComponent']['district']
                poi.stree = regeo['addressComponent']['township']
                pois.append(poi)       
            except Exception as e:
                logging.error("error while parse data")
                logging.error(e)
                continue
        return pois
    
    
    
        

    
#------        

class TencentMap(BaseMap):
    '''
    #具体的地图类：腾讯地图
    '''                
    
    def __init__(self):
        #self.KEY = '56SBZ-VEPWV-HSDPF-US3FK-HH4G6-JPFQ7'
        #self.KEY = 'JAGBZ-IQU3X-YJR4A-7S64I-HSZHK-6QBDI'
        self.KEY = 'SRBBZ-LAMRX-UQU43-ZSNWH-B257J-WQFTN'
        self.SEARCH_URL = 'http://apis.map.qq.com/ws/place/v1/search?'
        self.REGEO_URL = 'http://apis.map.qq.com/ws/geocoder/v1/?'
        self.size = 20
        
    def _conReUrl(self, location):
        '''
        #腾讯：逆地址解析URL
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
        #腾讯：构建按照行政区域搜索的URL
        '''
        #腾讯地图没有对中国进行编码，需进行特殊处理
        if region == 100000:
            region = '中国'
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
        #腾讯：构建按照矩形区域搜索的URL
        #region = [左下lng,左下lat,右上lng,右上lat]
        '''
        SEARCH_PARA = {
            'key':self.KEY,
            'boundary':'rectangle(左下lat,左下lng,右上lat,右上lng)' ,
            'keyword':'学校',
            'page_size':'20',
            'page_index':'1',
            }
        SEARCH_PARA['boundary'] = 'rectangle(%f,%f,%f,%f)'%(region[1],region[0],region[3],region[2])
        SEARCH_PARA['page_index'] = index
        SEARCH_PARA['keyword'] = keyword
        url = self.SEARCH_URL + urlencode(SEARCH_PARA)
        return url
    
    def getSub(self,region):
        '''
        #腾讯：获取实时行政子区域
        '''
        #腾讯没有对中国进行编码，需要做特殊处理
        if int(region) == 100000:
            url = 'http://apis.map.qq.com/ws/district/v1/list?key='+self.KEY
        else:
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
        #腾讯：返回结果条数，0：无,n：n,-1：溢出。
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
        #腾讯：解析结果的状态
        '''
        if res == None:
            return False,"conn error"
        if int(res['status']) != 0:
            return False,res['message']
        return True,'ok'    

    def parser(self, res):
        '''
        #腾讯：解析结果，并做逆地址解析
        '''
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
                    logging.error("failed request: %s,%s"%(msg,rURL))
                    return False
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
        #百度：逆地址解析URL
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
        '''
        #百度：获取子行政区域
        #由于百度不支持使用citycode进行搜索，用中文作为区域，相同名称区域会有干扰
        '''
        pass
    
    
    def _conBoxUrl(self, keyword, region, index):
        '''
        #百度：构建按照矩形区域搜索的URL
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
        #百度：返回结果条数，0：无,n：n,-1：溢出。
        '''
        if not res:
            return 0
        count = int(res['total'])
        if count >= 400:
            count = -1
        return count
    
    def getStatue(self, res):
        '''
        #百度：解析结果的状态
        '''
        if res == None:
            return False,"conn error"
        if int(res['status']) != 0:
            return False,res['message']
        return True,'ok'
    
    
    def getSub(self,region):
        '''
        #百度：获取实时行政子区域
        '''
        key = '56SBZ-VEPWV-HSDPF-US3FK-HH4G6-JPFQ7'
        url = 'http://apis.map.qq.com/ws/district/v1/getchildren?&id=%s&key=%s' % (region, key)
        res = self.request(url)
        stat,msg = self.getStatue(res)
        if not stat:
            logging.error("获取行政子区域失败 %s,%s"%(msg,url))
            return None
        sub = []
        for d in res['result'][0]:
            sub.append(d['id'])
        return sub
    
    def parser(self, res):
        '''
        #百度：解析结果，并进行逆地址解析
        '''
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
                    logging.error("failed request: %s,%s" % (msg,rURL))
                    return False
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
    elif mapType == '高德':
        return GaodeMap()