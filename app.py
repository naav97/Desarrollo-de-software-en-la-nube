from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from modelos import db
from vistas import TareaResource, TareaBorrarResource, VistaSignIn, VistaLogIn

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:toor@localhost/flask_db'
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
api.add_resource(TareaResource, '/tasks')
api.add_resource(TareaBorrarResource, '/tasks/<int:tarea_id>')
api.add_resource(VistaSignIn, '/signin')
api.add_resource(VistaLogIn, '/login')

if __name__=="__main__":
    app.run(port=5001)
