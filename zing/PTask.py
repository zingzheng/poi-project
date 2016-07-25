# -*- coding: utf-8 -*-
'''
Created on 2016年6月14日

@author: zingzheng
@blog: http://www.zing.ac.cn
@email: zing.ac@163.com
'''
import os
import datetime
import zing.Util as myUtil
import shapefile
from shapely.geometry import Polygon,shape

from zing.Util import logging,getProvinces
from zing import MapDi

BASE_PATH = os.path.split(os.path.realpath(__file__))[0] + '/../res/'
R_PATH = os.path.split(os.path.realpath(__file__))[0] + '/..'



class BaseTask(object):
    '''
    #任务的基类
    #目前子类有两种：按网格切分的任务，按照行政区域切分的任务
    '''
    
    def __init__(self,args):
        self.grid = [100,20,10]
        self.core_type = args[0]
        self.map_type = args[1]
        self.region_type = int(args[2])
        self.region = args[3]
        self.keyword = args[4]
        self.delta = args[5]
        self.nex = self.up_to_now(args[6])
        self.fp = '-'.join([self.core_type, self.map_type, self.keyword, self.region, self.str_now()])
        if len(args) == 7:
            self.recover = ''
            self.filePath = self.fp+'.txt'
        elif len(args) == 8:
            self.recover = args[7]
            self.filePath = self.fp+'.txt'
        else:
            self.recover = args[7]
            self.filePath = args[8]
        #等任务执行时再分配boxsPath
        self.boxsPath = ''
        
    def readBoxs(self):
        '''
        #读取还未完成的任务
        boxs有可能是网格，也有可能是
        '''
        boxs = []
        if not self.recover:
            return boxs
        else:
            with open(BASE_PATH+self.recover, 'r') as f:
                for line in f:
                    li = line.split('\n')[0].split(' ')
                    if len(li) == 1:
                        boxs.append(li[0])
                    else:
                        boxs.append([float(i) for i in li])
        return boxs
    
    def writeBoxs(self, boxs):
        '''
        #将未完成的任务写入文件
        '''
        self.boxsPath = self.fp+'.boxs'
        with open(BASE_PATH+self.boxsPath, 'w') as f:
            for box in boxs:
                if type(box) == type('10000'):
                    f.write(box)
                else:
                    f.write(' '.join([str(i) for i in box]))
                f.write('\n')
        
    def str_now(self):
        return datetime.datetime.now().strftime('%Y%m%d%H%M')
       
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
        taskList =  [self.core_type,self.map_type,self.region_type, self.region, self.keyword, self.delta, self.nex]
        if self.boxsPath:
            taskList.extend([self.boxsPath,self.filePath])
        return taskList
    
    def toStr(self):
        return ' '.join([str(s) for s in self.toList()])
    
    def dumpFile(self,datas):
        '''
        #将结果一次性写入文件
        '''
        with open(BASE_PATH+self.filePath,'a',encoding = 'utf-8') as f:
            for data in datas:
                f.write(self.keyword + ',' + data)
                f.write('\n')
    
    def run(self):
        '''
        #抽象方法，根据任务类型具体实现
        '''
        pass


    
    

class SubTask(BaseTask):
    '''
    #以行政区域划分的任务类
    '''

    def __init__(self,args):
        super().__init__(args)
        
        
    def run(self):
        '''    
        #程序入口，执行该任务，请自行判断任务是否到钟执行
        '''
        mapdi = MapDi.map_fac(self.map_type)
        if not self.recover:
            regions = [self.region]
        else:
            logging.info('正在从断点恢复。。。')
            regions = self.readBoxs()
            self.writeBoxs(regions)
            if self.recover and 'BASE' not in self.recover and os.path.exists(BASE_PATH+self.recover):
                os.remove(BASE_PATH+self.recover)
        while regions:
            print(regions)
            self.writeBoxs(regions)
            r = regions.pop()
            page,size,count = 0, mapdi.size, mapdi.size
            while page*size < count:
                page += 1
                while mapdi.SEARCH_KEY:
                    url = mapdi.conSearchUrl(self.keyword, r, page)
                    res = mapdi.request(url)
                    stat,msg = mapdi.getStatue(res)
                    if stat == 1:
                        break
                    elif stat == -1:
                        logging.error("error %s,%s"%(msg,url))
                        return False
                    else:
                        mapdi.SEARCH_KEY.pop(0)
                        logging.warn("error %s,%s"%(msg,url))
                        logging.info("该key失效，自动替换key。")
                if not mapdi.SEARCH_KEY:
                    logging.error("抓取失败，key已经用完")
                    return False
                count = mapdi.getCount(res)
                if count == 0:
                    break
                elif count == -1:
                    regions.extend(mapdi.getSub(r))
                    break
                else:
                    logging.info("running %s"%(url))
                    pois = mapdi.parser(res)
                    if pois == False:
                        return False
                    datas = []
                    for poi in pois:
                        datas.append(poi.toString())
                        print(poi.toString())
                    self.dumpFile(datas)
        self.dumpFile(['FINISH'])
        if self.boxsPath and os.path.exists(BASE_PATH+self.boxsPath):
            os.remove(BASE_PATH+self.boxsPath)
        self.recover, self.boxsPath, self.filePath = '', '', ''
        return True

    
#--------------  

class CircleTask(BaseTask):
    '''
    #以圆形区域划分的任务类
    #当前仅支持谷歌查找国家区域
    '''
    def __init__(self,args):
        super().__init__(args)
        self.shape = self._getShape(self.region)
        self.bbox = self.shape.bbox
        self.radius = 10
        
    
    def _getShape(self, region):
        '''
        #获取当前任务目标地区的多边形范围
        '''
        sf = shapefile.Reader(R_PATH+'/GADM/WORLD/TM_WORLD_BORDERS-0.3.shp')
        shapeRec = None
        for shapeRec in sf.iterShapeRecords():
            if shapeRec.record[4] == region: # country name stored in 5-th field ['TW', 'TW', 'TWN', 158, 'Taiwan', 0, 0, 0, 0, 120.946, 23.754]
                return shapeRec.shape
    
    def _getSub(self,location):
        pass
    
    def run(self):
        '''    
        #程序入口，执行该任务，请自行判断任务是否到钟执行
        '''
        if not self.recover:
            logging.info('正在切割圆形网格。。。')
            self.bboxs = myUtil.cutC(self.bbox, Polygon(self.shape.points), self.radius)
            #myUtil.showUp(self.shape.points,self.bboxs)
        else:
            logging.info('正在从断点恢复。。。')
            self.bboxs = self.readBoxs()
            self.writeBoxs(self.bboxs)
            if self.recover and 'BASE' not in self.recover and  os.path.exists(BASE_PATH+self.recover):
                os.remove(BASE_PATH + self.recover)
        mapdi = MapDi.map_fac(self.map_type)
        while self.bboxs:
            self.writeBoxs(self.bboxs)
            bbox = self.bboxs.pop()
            print(len(self.bboxs))
            while mapdi.SEARCH_KEY:
                res = mapdi.places(self.keyword, bbox[:2], bbox[2])
                print(res)
                stat,msg = mapdi.getStatue(res)
                if stat == 1:
                    break
                elif stat == -1:
                    logging.error("error %s,%s"%(msg))
                    return False
                else:
                    mapdi.SEARCH_KEY.pop(0)
                    logging.warn("error %s,%s"%(msg))
                    logging.info("该key失效，自动替换key。")
            if not mapdi.SEARCH_KEY:
                logging.error("抓取失败，key用完")
                return False
            
            ##递归
            if mapdi.getCount(res) == -1:
                self.bboxs.extend(myUtil.reCutC(bbox))
                continue
            
            datas = []
            pois = mapdi.parser(res)
            if pois == False:
                return False
            for poi in pois:
                poi = ','.join(poi)
                print(poi)
                datas.append(poi)
            self.dumpFile(datas)
        self.dumpFile(['FINISH'])
        
        if self.boxsPath and os.path.exists(BASE_PATH+self.boxsPath):
            os.remove(self.boxsPath)
            
        self.recover, self.boxsPath, self.filePath = '', '', ''
        return True
    
    

#----------------

class CutTask(BaseTask):
    '''
    #以网格划分的任务类
    '''
    def __init__(self,args):
        super().__init__(args)
        if self.region_type == 0:
            self.province, self.city = '', ''
        elif self.region_type == 1:
            self.province, self.city = self.region, ''
        else:
            self.province, self.city = self.region.split('@')
        self.shape = self._getShape()
        self.bbox = self.shape.bbox
        

    def _getShape(self):
        '''
        #获取当前任务目标地区的多边形范围
        '''
        if self.region_type == 0:
            sf = shapefile.Reader(R_PATH + "/GADM/CHN_adm0.shp")
            shape = sf.shapes()[0]
        elif self.region_type == 1:
            sf = shapefile.Reader(R_PATH + "/GADM/CHN_adm1.shp")
            index = myUtil.regionIndex(self.province)
            shape = sf.shapes()[index]
        else:
            sf = shapefile.Reader(R_PATH + "/GADM/CHN_adm2.shp")
            sf_properties = shapefile.Reader(R_PATH + "/GADM/CHN_adm2.dbf")
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
        if self.region_type == 0:
            return True
        for s in self.region.split('@'):
            if s not in address:
                return False
        return True
    
    
    
    def run(self):
        '''    
        #程序入口，执行该任务，请自行判断任务是否到钟执行
        '''
        if not self.recover:
            logging.info('正在切割网格。。。')
            if self.region_type == 0:
                isall = True
            self.bboxs = myUtil.cut(self.bbox, Polygon(self.shape.points), self.grid[self.region_type], isall)
        else:
            logging.info('正在从断点恢复。。。')
            self.bboxs = self.readBoxs()
            self.writeBoxs(self.bboxs)
            if self.recover and 'BASE' not in self.recover and  os.path.exists(BASE_PATH+self.recover):
                os.remove(BASE_PATH + self.recover)
        mapdi = MapDi.map_fac(self.map_type)
        while self.bboxs:
            self.writeBoxs(self.bboxs)
            bbox = self.bboxs.pop()
            print(len(self.bboxs))
            page,size,count = 0, mapdi.size, mapdi.size
            while page*size < count:
                page += 1
                while mapdi.SEARCH_KEY:
                    url = mapdi.conSearchUrl(self.keyword, bbox, page)
                    res = mapdi.request(url)
                    stat,msg = mapdi.getStatue(res)
                    if stat == 1:
                        break
                    elif stat == -1:
                        logging.error("error %s,%s"%(msg,url))
                        return False
                    else:
                        mapdi.SEARCH_KEY.pop(0)
                        logging.warn("error %s,%s"%(msg,url))
                        logging.info("该key失效，自动替换key。")
                if not mapdi.SEARCH_KEY:
                    logging.error("抓取失败，key用完")
                    return False
                count = mapdi.getCount(res)
                if count == 0:
                    break
                elif count == -1:
                    self.bboxs.extend(myUtil.cut(bbox, None, 2))
                    break
                else:
                    logging.info("running %s"%(url))
                    datas = []
                    pois = mapdi.parser(res)
                    if pois == False:
                        return False
                    for poi in pois:
                        print(poi.toString())
                        if self.check(poi.address):
                            datas.append(poi.toString())
                    self.dumpFile(datas)
        self.dumpFile(['FINISH'])
        
        if self.boxsPath and os.path.exists(BASE_PATH+self.boxsPath):
            os.remove(self.boxsPath)
            
        self.recover, self.boxsPath, self.filePath = '', '', ''
        return True


class CutProTask(CutTask):
    '''
    #专门负责将全国任务分解为省份任务
    #省份之间可能会存在区域重叠
    '''
    def __init__(self,args):
        super().__init__(args)
    
    def run(self):
        '''    
        #程序入口，执行该任务，请自行判断任务是否到钟执行
        '''
        self.bboxs = []
        if not self.recover:
            logging.info('正在切割网格。。。')
            #对每个省份切分网格
            for r in getProvinces():
                sf = shapefile.Reader(R_PATH + "/GADM/CHN_adm1.shp")
                index = myUtil.regionIndex(r)
                shape = sf.shapes()[index]
                bbox = shape.bbox
                self.bboxs.extend(myUtil.cut(bbox, Polygon(shape.points), self.grid[1]))
        else:
            logging.info('正在从断点恢复。。。')
            self.bboxs = self.readBoxs()
            self.writeBoxs(self.bboxs)
            if self.recover and 'BASE' not in self.recover and os.path.exists(BASE_PATH+self.recover):
                os.remove(BASE_PATH+self.recover)
        mapdi = MapDi.map_fac(self.map_type)
        while self.bboxs:
            self.writeBoxs(self.bboxs)
            bbox = self.bboxs.pop()
            print(len(self.bboxs))
            page,size,count = 0, mapdi.size, mapdi.size
            while page*size < count:
                page += 1
                while mapdi.SEARCH_KEY:
                    url = mapdi.conSearchUrl(self.keyword, bbox, page)
                    res = mapdi.request(url)
                    stat,msg = mapdi.getStatue(res)
                    if stat == 1:
                        break
                    elif stat == -1:
                        logging.error("error %s,%s"%(msg,url))
                        return False
                    else:
                        mapdi.SEARCH_KEY.pop(0)
                        logging.warn("error %s,%s"%(msg,url))
                        logging.info("该key失效，自动替换key。")
                if not mapdi.SEARCH_KEY:
                    logging.error("抓取失败，key用完")
                    return False
                count = mapdi.getCount(res)
                if count == 0:
                    break
                elif count == -1:
                    self.bboxs.extend(myUtil.cut(bbox, None, 2))
                    break
                else:
                    logging.info("running %s"%(url))
                    datas = []
                    pois = mapdi.parser(res)
                    if pois == False:
                        return False
                    for poi in pois:
                        print(poi.toString())
                        if self.check(poi.address):
                            datas.append(poi.toString())
                    self.dumpFile(datas)
        self.dumpFile(['FINISH'])
        if self.boxsPath and os.path.exists(BASE_PATH+self.boxsPath):
            os.remove(BASE_PATH+self.boxsPath)
        self.recover, self.boxsPath, self.filePath = '', '', ''
        return True
    

            
            
            
            

def taskFac(args):
    '''
    #静态方法，任务工厂类
    '''
    s = int(args[0])
    if s == 0:
        return CutTask(args)
    elif s == 1:
        return SubTask(args)
    elif s == 2:
        return CutProTask(args)
    elif s == 3:
        return CircleTask(args)