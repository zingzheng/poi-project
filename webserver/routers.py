# -*- coding: utf-8 -*-
'''
@author: zingzheng
'''

from flask import *

app = Flask(__name__)




@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' in session and session['username']:
        return render_template('home.html')
    else:
        return redirect(url_for('signin'))

@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('signin.html')

@app.route('/signin', methods=['POST'])
def signin():
    username = request.form['username']
    password = request.form['password']
    if username=='admin' and password=='admin':
        session['username'] = username
        return render_template('home.html')
    return render_template('signin.html', message='Bad username or password', username=username)


@app.route('/signout')
def signout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return render_template('signin.html')

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3sdfasdf09(N]LWX/,?RT'
    app.debug = True
    app.run(host='0.0.0.0')