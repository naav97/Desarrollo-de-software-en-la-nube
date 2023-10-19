from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

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