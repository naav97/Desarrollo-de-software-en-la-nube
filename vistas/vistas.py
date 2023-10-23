import os
import subprocess
import hashlib
from modelos import db, Usuario, Tarea, TareaSchema, UsuarioSchema
from flask_restful import Resource
from flask import request, send_from_directory, url_for
from celery import shared_task
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

tarea_schema = TareaSchema()
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

class TareasResource(Resource):
    @jwt_required()
    def get(self):
        id_usuario = get_jwt_identity()
        tareas = Tarea.query.filter_by(id_usuario=id_usuario)
        
        return tareas_schema.dump(tareas), 200

    @jwt_required()
    def post(self):
        id_usuario = get_jwt_identity()

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
                    id_usuario=id_usuario
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
    def get(self, tarea_id):
        id_usuario = get_jwt_identity()

        tarea = Tarea.query.filter_by(id=tarea_id, id_usuario=id_usuario).first()

        if tarea:
            return {"Tarea":tarea_schema.dump(tarea), "URL": "http://localhost:5001/api/download/" + tarea.archivo_nuevo}, 200
        else:
            return {"message": "Tarea no encontrada"}, 404

class TareaBorrarResource(Resource):
    @jwt_required()
    def delete(self, tarea_id):
        id_usuario = get_jwt_identity()

        tarea = Tarea.query.filter_by(id=tarea_id, id_usuario=id_usuario).first()

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

class VistaSignUp(Resource):
    def post(self):
        usuario = Usuario.query.filter_by(usuario=request.json['username']).first()
        if usuario is None:
            contrasena1 = request.json['password1']
            contrasena2 = request.json['password2']
            
            if contrasena1 != contrasena2:
                return {"message": "Las contraseñas no coinciden"}, 409
            
            contrasena_encriptada = hashlib.md5(contrasena1.encode('utf-8')).hexdigest()
            correo = request.json['email']
            nuevo_usuario = Usuario(usuario=request.json['username'], contrasena=contrasena_encriptada, correo=correo)
            db.session.add(nuevo_usuario)
            db.session.commit()
            return {"message": "Usuario creado con éxito", "id":nuevo_usuario.id, "correo":nuevo_usuario.correo}, 201
        else:
            return {"message": "Usuario ya existe"}, 409
    
    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.contrasena= request.json.get('password1', usuario.contrasena)
        db.session.commit()
        return usario_schema.dump(usuario)
    
    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204

class VistaLogIn(Resource):

    def post(self):
        contrasena_encriptada = hashlib.md5(request.json['password'].encode('utf-8')).hexdigest()
        usuario = Usuario.query.filter(Usuario.usuario == request.json['username'], Usuario.contrasena == contrasena_encriptada).first()

        db.session.commit()

        if usuario is None:
            return {"mensaje": "Usuario o contraseña ingresado es incorrecto"}, 401
        else:
            additional_claims = {"correo": usuario.correo}
            print(additional_claims)
            token_de_acceso = create_access_token(identity=usuario.id, additional_claims=additional_claims)
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso}, 200
        
class VistaDownload(Resource):
    def get(self, filename):
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
