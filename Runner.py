# -*- coding: utf-8 -*-
'''
Created on 2016年6月14日

@author: zingzheng
@blog: http://www.zing.ac.cn
@email: zing.ac@163.com

可根据需要在不同目录下创建多个Runner.py注意修改import的路径即可。  
task.txt文件格式：列和列之间用空格分开，行最后不要有多余的空格，不要有多的空行
列0- 切割方法 0：网格切割 1：行政区域切割
列1- 地图类型 百度、腾讯、高德
列2- 地区类型 0：全国；1：省；2：市
列3- 地区名称 若列2值为0：中国；若列2值为1：广东（不要带省字）；若列2值为2：广东@广州（不要带省和区）
列4- 执行间隔 1（最短间隔为1天）
列5- 执行日期 20160606（格式为：yyyymmdd，可空缺，表示今天）
'''

import os
import time
from zing import PTask
from zing.Util import logging


BASE_PATH = os.path.split(os.path.realpath(__file__))[0]
taskPath = BASE_PATH+'/task.txt'



def run():
    '''
    #启动方法
    '''
    while True:
        logging.info("aweak!")
        tasks = []
        logging.info("正在读取任务...")
        # 读取任务文件，并解析为任务类
        with open(taskPath, 'r', encoding = 'utf-8') as f:
            for line in f:
                if len(line) < 5 or '#' in line:
                    continue
                args = line.split('\n')[0].rstrip().split(' ')
                tasks.append(PTask.taskFac(args))
        logging.info("任务读取成功！")
        logging.info("开始执行任务....")
        for task in tasks:
            if task.isTime():
                logging.info('正在执行： %s'%(task.toStr()))
                if task.run():
                    logging.info('SUCCESS! %s' %(task.toStr()))
                    task.goNex()
                else:
                    logging.error('FAILED! %s' %(task.toStr()))
        logging.info("任务执行结束！")
        logging.info("开始更新任务状态....")
        with open(taskPath, 'w', encoding = 'utf-8') as f:
            for task in tasks:
                f.write(task.toStr())
                f.write('\n')
        logging.info("任务更新完成....")
        logging.info("sleeping!")
        time.sleep(60*60*2)    
        
if __name__ == '__main__':
    run()   