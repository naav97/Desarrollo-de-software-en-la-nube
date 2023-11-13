import os
import subprocess
from celery import Celery
from modelos import Tarea
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


app = Celery(broker= "redis://redis:6379/0",backend= "redis://redis:6379/0")
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:contraseña@db:5432/conversor'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['PROPAGATE_EXCEPTIONS'] = True
# app.config['SQLALCHEMY_ECHO'] = True

db_uri = 'postgresql://postgres:contraseña@db:5432/conversor'
engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)
session = Session()

@app.task(name="process_file")
def process_file(old_filename, new_filename, taskId):
    uploaded_file = os.path.join('./uploads', old_filename)
    processed_file = os.path.join('./uploads', new_filename)
    cmd = ['ffmpeg', '-i', uploaded_file,  processed_file]
    task = session.query(Tarea).filter_by(id=taskId).first()
    # task = Tarea.query.filter(Tarea.id == taskId).first()
    try:
        subprocess.run(cmd, check=True)
        print("Procesando tarea")
        task.estado = "processed"
        session.commit()
        return True
    except Exception as e:
        task.estado = "failed"
        session.commit()
        return str(e)
