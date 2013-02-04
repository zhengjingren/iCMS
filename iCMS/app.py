from flask import Flask
from flask import request, url_for
from flask.ext.misaka import Misaka
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)

db = SQLAlchemy(app)
Misaka(app)


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page


@app.template_filter('get_name')
def get_name(id):
    from .models import User
    return User.query.get(id).username

