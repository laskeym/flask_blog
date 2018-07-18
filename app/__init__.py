from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

from elasticsearch import Elasticsearch

app = Flask(__name__)
app.config.from_object(Config)

app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
if app.config['ELASTICSEARCH_URL'] else None

db = SQLAlchemy(app)

from app import models
from app.views import views
