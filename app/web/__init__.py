# -*- coding: utf-8 -*-
import sys
import os
import locale

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from app.settings import local as settings

# locale.setlocale(locale.LC_ALL, 'en_EN.utf8')
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(
		"app",
        template_folder='%s/%s' % (os.getcwd(), settings.TEMPLATE_FOLDER),
        static_folder='%s/%s' % (os.getcwd(), settings.STATIC_FOLDER),
        static_url_path='/static'
    )

app.secret_key = 'A0sZr98j/3yX R~XHH!jmN]LWX/,?RT'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////%s/app/db/arduino.db' % os.getcwd()
db = SQLAlchemy(app)

from app.helpers import filters

import logging
from logging.handlers import RotatingFileHandler
from logging import Formatter
logger = RotatingFileHandler('/mnt/sda1/dev/arduino/arduino.log', maxBytes=100*1000)
logger.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s'))
app.logger.addHandler(logger)
app.logger.setLevel(logging.INFO)

if not settings.INIT:
	from app.web.common_view import *
	from app.web.sensor_view import *
	from app.web.gateway_view import *
