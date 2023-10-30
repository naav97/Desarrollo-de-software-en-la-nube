import os
import subprocess
from celery import Celery
from modelos import Tarea
from modelos import db


app = Celery(broker= "redis://redis:6379/0",backend= "redis://redis:6379/0")

@app.task(name="process_file")
def process_file(old_filename, new_filename, taskId):
    uploaded_file = os.path.join('./uploads', old_filename)
    processed_file = os.path.join('./uploads', new_filename)
    cmd = ['ffmpeg', '-i', uploaded_file,  processed_file]
    task = Tarea.query.filter(Tarea.id == taskId).first()
    try:
        subprocess.run(cmd, check=True)
        print("Procesando tarea")
        task.estado = "processed"
        db.session.commit()
        return True
    except Exception as e:
        task.estado = "failed"
        db.session.commit()
        return str(e)
