# -*- coding: utf-8 -*-
'''
@author: zingzheng
'''

from flask import *
import os

app = Flask(__name__)



def authCheck():
    '''
    #用户登录态校验，若未登录自动转到登录页面
    '''
    if 'username' in session and session['username']:
        return True
    else:
        return False
        

@app.route('/', methods=['GET', 'POST'])
def home():
    '''
    #主页
    '''
    if authCheck():
        return render_template('home.html')
    else:
        return redirect(url_for('signin'))
    

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
        return render_template('home.html')
    return render_template('signin.html', error='Bad username or password', username=username)

@app.route('/signout')
def signout():
    '''
    #处理登出请求
    '''
    session.pop('username', None)
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3sdfasdf09(N]LWX/,?RT'
    app.debug = True
    app.run(host='0.0.0.0')