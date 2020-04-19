from flask import Blueprint, render_template
from jinja2 import TemplateNotFound

from app.forms.login import LoginForm

simple_page = Blueprint('simple_page', __name__)

values = {
        'slider1': 25,
        'slider2': 0,
        }

@simple_page.route('/')
@simple_page.route('/index')
def index():
    user = {'username': 'Lucas'}
    return render_template('index.html', **values)
