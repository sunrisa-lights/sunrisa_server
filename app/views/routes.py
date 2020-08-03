from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

simple_page = Blueprint(__name__)


@simple_page.route("/")
def show(page):
    # stuff
    print("Test")
