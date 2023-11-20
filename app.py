from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from modelos import db
from vistas import TareasResource, TareaResource, TareaBorrarResource, VistaSignUp, VistaLogIn, VistaDownload
from flask_jwt_extended import JWTManager
from google.cloud.sql.connector import Connector, IPTypes
from google.cloud import pubsub

# initialize pubsub publisher
publisher = pubsub.PublisherClient()
topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id='misw4204-202315-grupo21',
    topic='conversor'
)

# initialize Python Connector object
connector = Connector()

# Python Connector database connection function
def getconn():
    conn = connector.connect(
        "project:region:instance", # Cloud SQL Instance Connection Name
        "pg8000",
        user="user",
        password="password",
        db="db_name",
        ip_type= IPTypes.PUBLIC  # IPTypes.PRIVATE for private IP
    )
    return conn


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"creator": getconn}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']= 'super-secreto'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['UPLOAD_FOLDER'] = '/home/giancarlo_corredor/bucket'

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(TareasResource, '/api/tasks', resource_class_kwargs={'pubsub_publisher': publisher, 'topic_name': topic_name})
api.add_resource(TareaResource, '/api/tasks/<int:tarea_id>')
api.add_resource(TareaBorrarResource, '/api/tasks/<int:tarea_id>')
api.add_resource(VistaSignUp, '/api/auth/signup')
api.add_resource(VistaLogIn, '/api/auth/login')
api.add_resource(VistaDownload, '/api/download/<string:filename>')

jwt = JWTManager(app)