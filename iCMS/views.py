# -*- coding: utf-8 -*-
import hashlib
from flask import g
from flask import render_template, request, redirect, url_for, session
from flask import abort
from flask.ext.misaka import markdown

from .app import app, db
from .models import User, Post
from iCMS import data


@app.route('/')
def index():
    # FUCK YOU, 闫叔
    g.active = 'index'
    return render_template('index.html')


@app.route('/xsh')
def xsh():
    # FUCK YOU, 闫叔
    g.active = 'xsh'
    return render_template('xsh.html', xshs=data.xsh)


@app.route('/st')
def nkst():
    # FUCK YOU, 闫叔
    g.active = 'nkst'
    return render_template('nkst.html', sts=data.st)


@app.route('/tx')
def zgtx():
    # FUCK YOU, 闫叔
    g.active = 'zgtx'
    return render_template('zgtx.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('write'))
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form["username"]
    password = request.form["password"]
    hash = hashlib.sha512(password+username).hexdigest()
    u = User.query.filter_by(username=username).first_or_404()
    if u.password == hash:
        session['username'] = request.form['username']
        return redirect(url_for('index'))


@app.route('/<name>')
def list(name):
    # 文章列表页.
    if name in data.xsh:
        g.active = 'xsh'
        s = '学生会'
        l = url_for('xsh')
    elif name in data.st:
        g.active = 'nkst'
        s = '社团'
        l = url_for('nkst')
    elif name in data.tx:
        g.active = 'zgtx'
        s = '纵观天下'
        l = url_for('zgtx')
    else:
        abort(404)



@app.route('/<name>/write', methods=['GET', 'POST'])
def write(name):
    if 'username' not in session:
        return redirect(url_for('login'))
    if name not in (data.xsh + data.st + data.tx):
        abort(404)
    if request.method == 'GET':
        return render_template('writer.html')
    author = User.query.filter_by(username=session["username"]).first_or_404()
    post = Post(
        title=request.form["title"],
        body=request.form["content"],
        tag=name,
        author=author
    )
    db.session.add(post)
    db.session.commit()
    return redirect('/')
    # TODO: 直接跳到文章正文


@app.route('/preview', methods=['POST'])
def preview():
    if 'username' not in session:
        return 'FUCK YOU.'
    return markdown(request.form["md"])
