from flask import Flask
from flask_cors import CORS

app = Flask('default')
app_context = app.app_context()
app_context.push()