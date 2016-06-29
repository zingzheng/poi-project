# -*- coding: utf-8 -*-
'''
Created on 2016年6月14日
@author: zingzheng
@blog: http://www.zing.ac.cn
@email: zing.ac@163.com
'''


#import matplotlib.pyplot as plt
from shapely.geometry import box
from pypinyin import lazy_pinyin
import os 
import logging

BASE_PATH = os.path.split(os.path.realpath(__file__))[0] + '/..'
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


# def showShape(points):
#     '''
#     #将由多点表示的多边形可视化
#     para:
#         points - [[x0,y0],[x1,y1]...]
#     '''
#     y = [p[0] for p in points]
#     x = [p[1] for p in points]
#     plt.plot(y,x, 'x')
#     plt.show()
# 
# 
# 
# def showBboxs(bboxs):
#     '''
#     #将由多个矩形可视化，暂时只能以两点表示矩形
#     para:
#         bboxs - [[y0,x0,y1,x1],...]
#     '''
#     bx,by=[],[]
#     for bbox in bboxs:
#         bx.append(bbox[1])
#         bx.append(bbox[3])
#         by.append(bbox[0])
#         by.append(bbox[2])
#     plt.plot(by,bx, 'o')
#     plt.show()
#     
#   
# def showUp(points,bboxs):
#     '''
#     #同时展示多边形和矩形，方便比较
#     ''' 
#     y = [p[0] for p in points]
#     x = [p[1] for p in points]
#     plt.plot(y,x, 'x')
#     bx,by=[],[]
#     for bbox in bboxs:
#         bx.append(bbox[1])
#         bx.append(bbox[3])
#         by.append(bbox[0])
#         by.append(bbox[2])
#     plt.plot(by,bx, 'o')
#     plt.show()

    

def cut(bbox, region_polygon ,n):
    '''
    #网格切分
    para：
        bbox：最大的方格(l_lng,l_lat,r_lng,r_lat)
        region_polygon:实际的区域多边形，用于排除和实际区域无交集的方格
        n:切分为n*n块
    return:
        [bbox]
    '''   
    l_lng,l_lat,r_lng,r_lat = bbox
    d_lng = (r_lng - l_lng)*1.0 / n
    d_lat = (r_lat - l_lat)*1.0 / n
    bboxs = []
    for i in range(n):
        for j in range(n):
            n_l_lng = l_lng + i * d_lng
            n_l_lat = l_lat + j * d_lat
            n_r_lng = n_l_lng + d_lng
            n_r_lat = n_l_lat + d_lat
            
            if (n_l_lat >= 18.15 and n_r_lat <= 27.2 and
                n_l_lng >= 73.55 and n_r_lng <= 97) \
                or (n_l_lat >= 18.15 and n_r_lat <= 39.3 and
                    n_l_lng >= 124 and n_r_lng <= 135) \
                or (n_l_lat >= 45.5 and n_r_lat <= 53.6 and
                    n_l_lng >= 91.2 and n_r_lng <= 114.75):
                continue
            
            elif (n_l_lat >= 23.5 and n_r_lat <= 41.5 and
                n_l_lng >= 99.0 and n_r_lng <= 116.5) \
                or (n_l_lat >= 30.5 and n_r_lat <= 42.6 and
                    n_l_lng >= 80.5 and n_r_lng <= 97.5) \
                or (n_l_lat >= 42.5 and n_r_lat <= 48.8 and
                    n_l_lng >= 120 and n_r_lng <= 129.5):
                bboxs.append([n_l_lng,n_l_lat,n_r_lng,n_r_lat])
                continue
            
            if region_polygon == None:
                bboxs.append([n_l_lng,n_l_lat,n_r_lng,n_r_lat])
            else:
                rect = box(n_l_lng,n_l_lat,n_r_lng,n_r_lat)
                if rect.intersects(region_polygon):
                    bboxs.append([n_l_lng,n_l_lat,n_r_lng,n_r_lat])
    return bboxs



def py(prov):
    '''
    #将行政区域的中文转化为对应的拼音
    para:
        prov - 行政名称，如：广东、广州 
    '''
    #prov = unicode(prov, "utf-8")
    if prov == u'陕西':
        return 'shaanxi'
    else:
        return "".join(lazy_pinyin(prov))

def getProvinces():
    '''
    #获取全国省份
    '''
    provinces = ("安徽","北京","重庆","福建","甘肃","广东","广西","贵州","海南",
                "河北","黑龙江","河南","湖北","湖南","江苏","江西","吉林","辽宁",
                "内蒙古","宁夏","青海","陕西","山东","上海","山西","四川","天津",
                "新疆","西藏","云南","浙江")
    return provinces


def regionIndex(prov):
    '''
    #将省份转化为对应的GADM序号
    para:
        prov - 省份名，如：广东
    '''
    province_to_index = {
        "anhui": 0,
        "beijing": 1,
        "chongqing": 2,
        "fujian": 3,
        "gansu": 4,
        "guangdong": 5,
        "guangxi": 6,
        "guizhou": 7,
        "hainan": 8,
        "hebei": 9,
        "heilongjiang": 10,
        "henan": 11,
        "hubei": 12,
        "hunan": 13,
        "jiangsu": 14,
        "jiangxi": 15,
        "jilin": 16,
        "liaoning": 17,
        "neimenggu": 18,
        "ningxia": 19,
        "qinghai": 20,
        "shaanxi": 21,
        "shandong": 22,
        "shanghai": 23,
        "shanxi": 24,
        "sichuan": 25,
        "tianjin": 26,
        "xinjiang": 27,
        "xizang": 28,
        "yunnan": 29,
        "zhejiang": 30
    }
    return province_to_index[py(prov)]

