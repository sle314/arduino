# -*- coding: utf-8 -*-
import sys
import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from app.settings import local as settings

# set encoding
reload(sys)
sys.setdefaultencoding('utf-8')

# create Flask app with template and static folder definitions
app = Flask(
		"app",
        template_folder='%s/%s' % (os.getcwd(), settings.TEMPLATE_FOLDER),
        static_folder='%s/%s' % (os.getcwd(), settings.STATIC_FOLDER),
        static_url_path='/static'
    )
# define secret key for sessions
app.secret_key = 'A0sZr98j/3yX R~XHH!jmN]LWX/,?RT'

# define and init database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////%s/app/db/arduino.db' % os.getcwd()
db = SQLAlchemy(app)

# import custom jinja filters
from app.helpers import filters

# define a rotating logger which saves 100MB of logs and then starts over
import logging
from logging.handlers import RotatingFileHandler
from logging import Formatter
logger = RotatingFileHandler('/mnt/sda1/dev/arduino/arduino.log', maxBytes=100*1024*1024)
logger.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s'))
app.logger.addHandler(logger)
app.logger.setLevel(logging.INFO)

# import views if we are starting the server and not initializing the db values
# import crashes initialization because of circular dependencies
if not settings.INIT:
	from app.web.common_view import *
	from app.web.sensor_view import *
	from app.web.gateway_view import *
