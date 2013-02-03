import datetime
import hashlib

from .app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, username, password):
        self.username = username
        self.password = hashlib.sha512(password+username).hexdigest()

    def __repr__(self):
        return '<User %r>' % self.username


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True)
    body = db.Column(db.Text, unique=True)
    pub_date = db.Column(db.DateTime)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tag = db.Column(db.String(80))


    def __init__(self, title, body, tag, author, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.datetime.utcnow()
        self.pub_date = pub_date
        self.tag = tag
        self.author_id = author.id

    def __repr__(self):
        return '<Post %r>' % self.title