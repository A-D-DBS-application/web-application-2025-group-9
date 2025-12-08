from flask import Blueprint, request, redirect, url_for, render_template, session
from .models import db

from flask import Blueprint, request, redirect, url_for, render_template, session
from .models import db

main = Blueprint("main", __name__)

# Example route
@main.route("/")
def index():
    return "Hello from Flask Blueprint!"