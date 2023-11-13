import os
import subprocess
from celery import Celery
from modelos import Tarea
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector, IPTypes

# initialize Python Connector object
connector = Connector()

# Python Connector database connection function
def getconn():
    conn = connector.connect(
        "checkurl-396803:us-central1:test01", # Cloud SQL Instance Connection Name
        "pg8000",
        user="user",
        password="password",
        db="db_name",
        ip_type= IPTypes.PUBLIC  # IPTypes.PRIVATE for private IP
    )
    return conn

app = Celery(broker= "redis://redis:6379/0",backend= "redis://redis:6379/0")

db_uri = 'postgresql://user:password@34.27.104.33:5432/conversor'
engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)
session = Session()

@app.task(name="process_file")
def process_file(old_filename, new_filename, taskId):
    uploaded_file = os.path.join('/home/naav972/videos', old_filename)
    processed_file = os.path.join('/home/naav972/videos', new_filename)
    cmd = ['ffmpeg', '-i', uploaded_file,  processed_file]
    cmd2 = ['gsutil', 'cp', processed_file, 'gs://test-dev-naav97']
    task = session.query(Tarea).filter_by(id=taskId).first()
    # task = Tarea.query.filter(Tarea.id == taskId).first()
    try:
        subprocess.run(cmd, check=True)
        subprocess.run(cmd2, check=True)
        print("Procesando tarea")
        task.estado = "processed"
        session.commit()
        return True
    except Exception as e:
        task.estado = "failed"
        session.commit()
        return str(e)

