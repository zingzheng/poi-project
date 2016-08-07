# -*- coding: utf-8 -*-
'''
@author: zingzheng
'''

from flask import *
import os
from webserver.mydao import *
from webserver.mybean import *
from contextlib import closing

app = Flask(__name__)





def authCheck():
    '''
    #用户登录态校验，若未登录自动转到登录页面
    '''
    if 'username' in session and session['username']:
        return True
    else:
        return False

@app.before_request
def before_request():
    #权限校验
    if request.endpoint not in ['signin','signin_page'] and not authCheck():
        return redirect(url_for('signin'))

@app.teardown_request
def teardown_request(exception):
    pass


@app.route('/', methods=['GET', 'POST'])
def home():
    '''
    #主页
    '''
    return render_template('home.html',jobs = JobInfoDao().select())

@app.route('/signin', methods=['GET'])
def signin_page():
    '''
    #展示登录页面
    '''
    return render_template('signin.html')

@app.route('/signin', methods=['POST'])
def signin():
    '''
    #处理登录请求
    '''
    username = request.form['username']
    password = request.form['password']
    if username=='admin' and password=='admin':
        session['username'] = username
        flash('signin success')
        return redirect('/')
    return render_template('signin.html', error='Bad username or password', username=username)

@app.route('/signout')
def signout():
    '''
    #处理登出请求
    '''
    session.pop('username', None)
    return redirect(url_for('signin'))

@app.route('/addJob', methods=['post'])
def addJob():
    job = JobInfoBean()
    job.core_type = request.form['core_type']
    job.map_type = request.form['map_type']
    job.region_type = request.form['region_type']
    job.region = request.form['region']
    job.keyword = request.form['keyword']
    JobInfoDao().insert(job)
    return redirect('/')
    

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3sdfasdf09(N]LWX/,?RT'
    app.debug = True
    init_all_db()
    app.run(host='0.0.0.0')