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
    g.use_slide = True
    return render_template('index.html')


@app.route('/xsh')
def xsh():
    # FUCK YOU, 闫叔
    g.active = 'xsh'
    g.use_slide = True
    return render_template('xsh.html', xshs=data.xsh)


@app.route('/st')
def nkst():
    # FUCK YOU, 闫叔
    g.active = 'nkst'
    g.use_slide = True
    return render_template('nkst.html', sts=data.st)


@app.route('/tx')
def zgtx():
    # FUCK YOU, 闫叔
    g.active = 'zgtx'
    g.use_slide = True
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


@app.route('/<name>', defaults={'page': 1})
@app.route('/<name>/page/<int:page>')
def list(name, page):
    # 文章列表页.
    if name in data.xsh:
        g.active = 'xsh'
        s = u'学生会'
        l = url_for('xsh')
    elif name in data.st:
        g.active = 'nkst'
        s = u'社团'
        l = url_for('nkst')
    elif name in data.tx:
        g.active = 'zgtx'
        s = u'纵观天下'
        l = url_for('zgtx')
    else:
        abort(404)
    posts = Post.query.filter_by(tag=name)
    posts = posts.order_by(Post.pub_date.desc()).paginate(page, per_page=20)
    return render_template('list.html', posts=posts, name=name,
        s=s, l=l)


@app.route('/<int:id>')
def post(id):
    post = Post.query.get(id)
    if post.tag in data.xsh:
        g.active = 'xsh'
        s = u'学生会'
        l = url_for('xsh')
    elif post.tag in data.st:
        g.active = 'nkst'
        s = u'社团'
        l = url_for('nkst')
    elif post.tag in data.tx:
        g.active = 'zgtx'
        s = u'纵观天下'
        l = url_for('zgtx')
    return render_template('article.html', post=post, s=s, l=l)


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
    return redirect(url_for('post', id=post.id))


@app.route('/preview', methods=['POST'])
def preview():
    if 'username' not in session:
        return 'o.'
    return markdown(request.form["md"])
