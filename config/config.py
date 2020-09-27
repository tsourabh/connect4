from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
import os
import datetime
from flask_mongoengine import MongoEngine

database = MongoEngine()
mode = ''
if not os.environ.get('mode', None):
    mode = 'development'
os.environ['ENV'] = mode


def initialize_db(_app):
    database.init_app(_app)


PORT = os.environ.get('PORT', '5000')
# SECRET_KEY = 'fn114v94f8#k+7(t9m(@kh9b=_6wshai!u#7bx%u*ojs=_ru*+'
app = Flask(__name__)


if os.environ.get("ENV") == 'development':
    # LOCAL DB SETTINGS
    DATABASE_NAME = 'connect4'
    HOST = 'mongodb://localhost/connect4'
    ALIAS = 'default'
    USERNAME = ''
    PASSWORD = ''
else:
    # PROD DB SETTINGS
    DATABASE_NAME = 'connect4'
    HOST = "mongodb+srv://root:" + os.environ.get(
        'mongo_password') + "@sharedit.61cic.mongodb.net/connect4?retryWrites=true&w=majority"
    ALIAS = 'default'
    USERNAME = 'root'
    PASSWORD = os.environ.get('mongo_password')


app.config['DEBUG'] = os.environ.get('ENV') == 'development'

# app.config['JWT_SECRET_KEY'] = SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

app.config['MONGODB_SETTINGS'] = {
    'db': DATABASE_NAME,
    'host': HOST,
    'alias': ALIAS,
    'username': USERNAME,
    'password': PASSWORD
}

flask_bcrypt = Bcrypt(app)
jwt = JWTManager(app)
