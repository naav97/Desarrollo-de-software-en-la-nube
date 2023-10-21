from modelos import db, Usuario, Tarea, TareaSchema
from flask_restful import Resource
from flask import request

tareas_schema = TareaSchema(many=True)

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
        pass