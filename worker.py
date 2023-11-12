import os
import subprocess
from celery import Celery
from modelos import Tarea
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google.cloud import storage
# from dotenv import load_dotenv

# load_dotenv()

#app = Celery(broker= "redis://redis:6379/0",backend= "redis://redis:6379/0")

#db_uri = 'postgresql://postgres:contraseña@db:5432/conversor'
#engine = create_engine(db_uri)
#Session = sessionmaker(bind=engine)
#session = Session()

# GCP_API_KEY = os.getenv('API_KEY')

bucket_name = "test-dev-naav97"
client = storage.Client(project="checkurl-396803")

#@app.task(name="process_file")
def process_file(old_filename, new_filename, taskId):
    # Descarga del archivo
    bucket = client.bucket(bucket_name)
    og_file_in_b = bucket.blob(old_filename)
    uploaded_file = os.path.join('./uploads', old_filename)
    og_file_in_b.download_to_file(uploaded_file)

    processed_file = os.path.join('./uploads', new_filename)
    #cmd = ['ffmpeg', '-i', uploaded_file,  processed_file]
    #task = session.query(Tarea).filter_by(id=taskId).first()
    # task = Tarea.query.filter(Tarea.id == taskId).first()
    try:
        #subprocess.run(cmd, check=True)
        print("Procesando tarea")
        #task.estado = "processed"
        #session.commit()
        return True
    except Exception as e:
        #task.estado = "failed"
        #session.commit()
        return str(e)

process_file("trump-drops-pen.webm", "test.webm", 34)
