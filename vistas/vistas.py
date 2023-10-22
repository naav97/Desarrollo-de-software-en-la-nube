import os
import subprocess
from modelos import db, Usuario, Tarea, TareaSchema, UsuarioSchema
from flask_restful import Resource
from flask import request
from werkzeug.utils import secure_filename
from celery import shared_task
from flask_jwt_extended import create_access_token, jwt_required
import hashlib

tareas_schema = TareaSchema(many=True)
usario_schema = UsuarioSchema()

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

class TareasResource(Resource):
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

class TareaResource(Resource):
    @jwt_required()
    def get(self, taskId):

        tarea = Tarea.query.get(taskId)

        if tarea:
            return {"Tarea":[tareas_schema.dumps(tarea)], "URL":[""]}, 200
        else:
            return {"message": "Tarea no encontrada"}, 404

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

class VistaSignIn(Resource):
    def post(self):
        usuario = Usuario.query.filter_by(usuario=request.json['usuario']).first()
        if usuario is None:
            contrasena_encriptada = hashlib.md5(request.json['contrasena'].encode('utf-8')).hexdigest()
            nuevo_usuario = Usuario(usuario=request.json['usuario'], contrasena=contrasena_encriptada)
            db.session.add(nuevo_usuario)
            db.session.commit()
            additional_claims = {"correo": nuevo_usuario.correo}
            token_de_acceso = create_access_token(identity=nuevo_usuario.id, additional_claims=additional_claims)
            return {"message": "Usuario creado con éxito", "id":nuevo_usuario.id, "correo":nuevo_usuario.correo, "token":token_de_acceso}, 201
        else:
            return {"message": "Usuario ya existe"}, 409
    
    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.contrasena= request.json.get('contrasena', usuario.contrasena)
        db.session.commit()
        return usario_schema.dump(usuario)
    
    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204

class VistaLogIn(Resource):

    def post(self):
        contrasena_encriptada = hashlib.md5(request.json['contrasena'].encode('utf-8')).hexdigest()
        usuario = Usuario.query.filter(Usuario.usuario == request.json['usuario'], Usuario.contrasena == contrasena_encriptada, Usuario.correo == request.json['correo']).first()

        db.session.commit()

        if usuario is None:
            return "El usuario no existe", 404
        else:
            additional_claims = {"correo": usuario.correo}
            print(additional_claims)
            token_de_acceso = create_access_token(identity=usuario.id, additional_claims=additional_claims)
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso, "id": usuario.id, "username": usuario.usuario, "idParent": usuario.parent_id}, 200