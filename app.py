from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from modelos import db
from vistas import TareasResource, TareaResource, TareaBorrarResource, VistaSignIn, VistaLogIn
from celery import Celery, Task

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:contraseña@db:5432/conversor'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']= 'super-secreto'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['CELERY'] = {
    "broker_url": "redis://localhost",
    "result_backend": "redis://localhost",
    "task_ignore_result": True,
}

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

celery_app = celery_init_app(app)

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(TareasResource, '/api/tasks')
api.add_resource(TareasResource, '/api/tasks/<int:tarea_id>')
api.add_resource(TareaBorrarResource, '/api/tasks/<int:tarea_id>')
api.add_resource(TareaBorrarResource, '/tasks/<int:tarea_id>')
api.add_resource(VistaSignIn, '/api/signin')
api.add_resource(VistaLogIn, '/api/login')

