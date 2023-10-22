import os
import subprocess
from modelos import db, Usuario, Tarea, TareaSchema
from flask_restful import Resource
from flask import request
from werkzeug.utils import secure_filename
from celery import shared_task

tareas_schema = TareaSchema(many=True)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'mp4', 'm4a', 'm4p', 'm4b', 'm4r', 'm4v', 'webm', 'avi', 'mpeg', 'wmv'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@shared_task(ignore_result=False)
def process_file(old_filename, new_filename, taskId):
    uploaded_file = os.path.join('./uploads', old_filename)
    processed_file = os.path.join('./uploads', new_filename)
    cmd = ['ffmpeg', '-i', uploaded_file,  processed_file]
    try:
        subprocess.run(cmd, check=True)
        task = Tarea.query.filter(Tarea.id == taskId).first()
        task.estado = "processed"
        db.session.commit()
        return True
    except Exception as e:
        return str(e)

class TareaResource(Resource):
    def get(self):
        tareas = Tarea.query.all()
        
        return tareas_schema.dump(tareas), 200

    def post(self):
        if 'archivo' not in request.files:
            return {"message": "Error no se envia archivo"}, 400
        if request.files['archivo'].filename == '':
            return {"message": "Error no se envia archivo"}, 400
        if allowed_file(request.files['archivo'].filename):
            nombreSec = secure_filename(request.files['archivo'].filename)
            request.files['archivo'].save(os.path.join(UPLOAD_FOLDER, nombreSec))
            nombreNuevo = nombreSec.rsplit('.', 1)[0]+'.'+request.form.get('formato')
            try:
                nuevaT = Tarea(
                    archivo_original=nombreSec,
                    archivo_nuevo=nombreNuevo,
                    formato_nuevo=request.form.get('formato'),
                    estado="uploaded",
                )
                db.session.add(nuevaT)
                db.session.commit()
                process_file.delay(nombreSec, nombreNuevo, nuevaT.id)
                return {"message": "Tarea creada"}, 201
            except Exception as e:
                db.session.rollback()
                return {"message": "Error: "+str(e)}, 500

class TareaBorrarResource(Resource):
    def delete(self, tarea_id):
        tarea = Tarea.query.get(tarea_id)

        if tarea:
            try:
                db.session.delete(tarea)
                db.session.commit()
                return {"message": "Tarea eliminada con éxito"}, 200
            except Exception as e:
                db.session.rollback()
                return {"message": "Error al eliminar la tarea"}, 500
        else:
            return {"message": "Tarea no encontrada"}, 404
