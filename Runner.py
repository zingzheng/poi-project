# -*- coding: utf-8 -*-
'''
Created on 2016年6月14日

@author: zingzheng
@blog: http://www.zing.ac.cn
@email: zing.ac@163.com

可根据需要在不同目录下创建多个Runner.py注意修改import的路径即可。  
task.txt文件格式：列和列之间用空格分开，行最后不要有多余的空格，不要有多的空行
列0- 切割方法 0：网格切割   1：行政区域切割  2：全国按照省份网格切分 3：圆形区域划分
列1- 地图类型 百度、腾讯、高德、谷歌
列2- 地区类型 0：全国；1：省；2：市
列3- 地区名称 若列2值为0：中国；若列2值为1：广东（不要带省字）；若列2值为2：广东@广州（不要带省和区）
列4- 执行间隔 1（最短间隔为1天）
列5- 执行日期 20160606 格式为：yyyymmdd
'''

import os
import time
from zing import PTask
from zing.Util import getLogger


BASE_PATH = os.path.split(os.path.realpath(__file__))[0]

class runner():
    def __init__(self): 
        self.taskPath = BASE_PATH+'/task.txt'
        self.logger  = getLogger('runner.log','runner')

    def readTask(self):
        tasks = []
        self.logger.info("正在读取任务...")
        # 读取任务文件，并解析为任务类
        with open(self.taskPath, 'r', encoding = 'utf-8') as f:
            for line in f:
                if len(line) < 5 or '#' in line:
                    continue
                args = line.split('\n')[0].rstrip().split(' ')
                tasks.append(PTask.taskFac(args))
        self.logger.info("任务读取成功！")
        return tasks

    def writeTask(self,tasks):
        self.logger.info("开始更新任务状态....")
        with open(self.taskPath, 'w', encoding = 'utf-8') as f:
            for task in tasks:
                f.write(task.toStr())
                f.write('\n')
        self.logger.info("任务更新完成....")
    
    



    def run(self):
        '''
        #启动方法
        '''
        try:
            while True:
                self.logger.info("aweak!")
                tasks = self.readTask()
                self.logger.info("开始执行任务....")
                for task in tasks:
                    if task.isTime():
                        self.logger.info('正在执行： %s'%(task.toStr()))
                        task.logger.info('正在执行： %s'%(task.toStr()))
                        self.writeTask(tasks)
                        if task.run():
                            self.logger.info('SUCCESS! %s' %(task.toStr()))
                            task.logger.info('SUCCESS! %s' %(task.toStr()))
                            task.goNex()
                        else:
                            self.logger.error('FAILED! %s' %(task.toStr()))
                            task.logger.error('FAILED! %s' %(task.toStr()))
                        self.writeTask(tasks)
                self.logger.info("任务执行结束！")
                self.logger.info("sleeping!")
                time.sleep(60*60*2)
        except Exception as e:
            self.logger.error('error in runner: %s'%(e))
            self.writeTask(tasks)    
        
if __name__ == '__main__':
    runner().run()