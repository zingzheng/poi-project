# -*- coding: utf-8 -*-
'''
Created on 2016年6月14日

@author: zingzheng
'''
import os
import datetime
import zing.Util as myUtil
import shapefile
from shapely.geometry import Polygon,shape

import logging
from zing import MapDi

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



class BaseTask(object):
    '''
    #任务的基类
    #目前子类有两种：按网格切分的任务，按照行政区域切分的任务
    '''
    
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
            
        fp = '-'.join([self.keyword, self.region, self.nex])
        self.filePath = BASE_PATH + '/res/'+fp+'.txt'
    
       
    def str_to_time(self, s):
        '''
        #字符串格式日期转datetime
        '''
        return datetime.datetime.strptime(s, '%Y%m%d')

    
    def time_to_str(self, t):
        '''
        #datetime格式日期转字符串
        '''
        return t.strftime('%Y%m%d')  


    def up_to_now(self, s_nex):
        '''
        #若时间已经过时，自动更新到当前
        '''
        now = datetime.datetime.now()
        nex = self.str_to_time(s_nex)
        if (now-nex).days > 0:
            return self.time_to_str(now)
        else:
            return s_nex


    def goNex(self):
        '''
        #更新下次执行时间
        '''
        self.nex = self.time_to_str(self.str_to_time(self.nex) + datetime.timedelta(days=int(self.delta)))
    
    
    def isTime(self):
        '''
        #判断当前任务是否需要被执行
        '''
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
    
    def run(self):
        '''
        #抽象方法，根据任务类型具体实现
        '''
        pass


    
    

class SubTask(BaseTask):
    '''
    #以行政区域划分的任务类
    '''

    def __int__(self):
        pass
    
    


class CutTask(BaseTask):
    '''
    #以网格划分的任务类
    '''
    
    def _init__(self,args):
        super(args)
        self.shape = self._getShape()
        self.bbox = self.shape.bbox
        self.bboxs = myUtil.cut(self.bbox, Polygon(self.shape.points), [100,50,10][self.rtype])
    

    def _getShape(self):
        '''
        #获取当前任务目标地区的多边形范围
        '''
        if self.rtype == 0:
            sf = shapefile.Reader(BASE_PATH + "/GADM/CHN_adm0.shp")
            shape = sf.shapes()[0]
        elif self.rtype == 1:
            sf = shapefile.Reader(BASE_PATH + "/GADM/CHN_adm1.shp")
            index = myUtil.regionIndex(self.province)
            shape = sf.shapes()[index]
        else:
            sf = shapefile.Reader(BASE_PATH + "/GADM/CHN_adm2.shp")
            sf_properties = shapefile.Reader(BASE_PATH + "/GADM/CHN_adm2.dbf")
            shapes = sf.shapes()
            records = sf_properties.records()
            for i in range(len(records)):
                if records[i][3] == myUtil.regionIndex(self.province) + 1 and myUtil.py(self.city) == records[i][6].lower().replace('\'', ''):
                    shape = shapes[i]
                    break   
        return shape
        
    
      
    def check(self, address):
        '''
        #检查地址address是否在任务的region内  
        '''
        for s in self.region.split('@'):
            if s not in address:
                return False
        return True
    
    def dumpFile(self,datas):
        '''
        #将结果一次性写入文件
        '''
        with open(self.filePath,'w') as f:
            f.writelines(datas)
    
    
    def run(self):
        '''    
        #程序入口，执行该任务，请自行判断任务是否到钟执行
        '''
        mapdi = MapDi.map_fac(self.map_type)
        datas = []
        while self.bboxs:
            bbox = self.bboxs.pop()
            page,size,count = 0, mapdi.size, mapdi.size
            while page*size < count:
                page += 1
                url = mapdi.conSearchUrl(self.keyword, bbox, page)
                res = mapdi.request(url)
                stat,msg = mapdi.getStatue(res)
                if not stat:
                    logging.ERROR("error %s,%s"%(url,msg))
                    return False
                count = mapdi.getCount(res)
                if count == 0:
                    break
                elif count == -1:
                    self.bboxs.extend(myUtil.cut(bbox, None, 2))
                    break
                else:
                    logging.info("running %s"%(url))
                    pois = mapdi.parser(res)
                    for poi in pois:
                        if self.check(poi.address):
                            datas.append(poi.toString())
        self.dumpFile(datas)
        return True


def taskFac(s,args):
    '''
    #静态方法，任务工厂类
    '''
    if int(s) == 0:
        return CutTask(args)
    else:
        return SubTask(args)