from flask.ext.sqlalchemy import SQLAlchemy
from app.web import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)