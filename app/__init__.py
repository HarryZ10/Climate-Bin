# Every level/folder of a Python application has an __init__.py file. The purpose of this file is to connect the levels
# of the app to each other. 

from mongoengine import *
from flask import Flask
import os
from flask_moment import Moment

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(20)
# you must change the next line to be link to your database at mlab
connect("<yourDBName>", host='mongodb://<user>:<password>@<somerandoNumber>.mlab.com:41643/<yourDBName>', retryWrites=False)
moment = Moment(app)

from .routes import *