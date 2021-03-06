import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # SQLALCHEMY
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{db}'\
            .format(db=os.path.join(basedir, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ELASTICSEARCH
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    
    # Blog config
    POSTS_PER_PAGE = 3
