import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development-key'
    MAX_CONTENT_LENGTH = 16 * 1000 * 1000
