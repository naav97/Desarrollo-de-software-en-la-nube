from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from modelos import db
from vistas import TareaResource, TareaBorrarResource

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:contraseña@db:5432/conversor'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']= 'super-secreto'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(TareaResource, '/api/tasks')
api.add_resource(TareaBorrarResource, '/api/tasks/<int:tarea_id>')

