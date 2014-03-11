# -*- coding: utf-8 -*-
import logging
import sys
import os
import locale

from flask import Flask

locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask("app",
            template_folder='%s/web/templates/' % os.getcwd(),
            static_folder='%s/web/' % os.getcwd(),
            static_url_path='/static'
    )

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


logger = logging.StreamHandler()

logger.setLevel(logging.INFO)
app.logger.addHandler(logger)
app.logger.setLevel(logging.INFO)

from common_view import *
