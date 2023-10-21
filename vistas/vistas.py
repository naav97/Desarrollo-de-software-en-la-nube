import os
from modelos import db, Usuario, Tarea, TareaSchema
from flask_restful import Resource
from flask import request
from datetime import datetime
from werkzeug.utils import secure_filename

tareas_schema = TareaSchema(many=True)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'mp4', 'm4a', 'm4p', 'm4b', 'm4r', 'm4v', 'webm', 'avi', 'mpeg', 'wmv'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            try:
                nuevaT = Tarea(
                    archivo_original=nombreSec,
                    formato_nuevo=request.form.get('formato'),
                    estado="uploaded",
                )
                db.session.add(nuevaT)
                db.session.commit()
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
