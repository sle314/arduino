# -*- coding: utf-8 -*-
import logging
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

logger = logging.StreamHandler()

logger.setLevel(logging.INFO)
app.logger.addHandler(logger)
app.logger.setLevel(logging.INFO)

from common_view import *
from sensor_view import *
from gateway_view import *
