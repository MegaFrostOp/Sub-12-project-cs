import os

class Config:
    SECRET_KEY = os.environ.get('SECRET KEY')
    DEBUG = True     # dude turn this to False when you are giving this as final product

