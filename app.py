from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

app = Flask('default')
app_context = app.app_context()
app_context.push()