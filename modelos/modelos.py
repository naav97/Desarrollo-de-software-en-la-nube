from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from datetime import datetime

db = SQLAlchemy()
Base = declarative_base()


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False)
    contrasena = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(50))
    parent_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    parent = db.relationship('Usuario', remote_side=[id])

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        load_instance = True
        include_relationships = True
        include_fk = True
    id = fields.String()


class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    archivo_original = db.Column(db.String(50), nullable=False)
    archivo_nuevo = db.Column(db.String(50), nullable=True)
    formato_nuevo = db.Column(db.String(5), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

class TareaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Tarea
        load_instace = True
    id = fields.String()
