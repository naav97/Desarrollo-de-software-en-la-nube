from modelos import db, Usuario, Tarea, TareaSchema, UsuarioSchema
from flask_restful import Resource
from flask import request
from flask_jwt_extended import create_access_token
import hashlib
import json

tareas_schema = TareaSchema(many=True)
usario_schema = UsuarioSchema()

class TareaResource(Resource):
    def get(self):
        tareas = Tarea.query.all()
        
        return tareas_schema.dump(tareas), 200

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

class VistaSignIn():
    def post(self):
        usuario = Usuario.query.filter_by(usuario=request.json['usuario']).first()
        if usuario is None:
            contrasena_encriptada = hashlib.md5(request.json['contrasena'].encode('utf-8')).hexdigest()
            nuevo_usuario = Usuario(usuario=request.json['usuario'], contrasena=contrasena_encriptada)
            db.session.add(nuevo_usuario)
            db.session.commit()
            return {"message": "Usuario creado con éxito"}, 201
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

class VistaLogIn():

    def post(self):
        contrasena_encriptada = hashlib.md5(request.json['contrasena'].encode('utf-8')).hexdigest()
        usuario = Usuario.query.filter(Usuario.usuario == request.json['usuario'], Usuario.contrasena == contrasena_encriptada).first()

        db.session.commit()

        if usuario is None:
            return "El usuario no existe", 404
        else:
            token_de_acceso = create_access_token(identity=usuario.id)
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso, "id": usuario.id, "username": usuario.usuario, "idParent": usuario.parent_id}, 200