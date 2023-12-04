import os
import subprocess
import time
import json
from modelos import Tarea
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector, IPTypes
from google.cloud import pubsub
from flask import Flask, request, jsonify

app = Flask(__name__)

# initialize Python Connector object
connector = Connector()

# Python Connector database connection function
def getconn():
    conn = connector.connect(
        "project:region:instance", # Cloud SQL Instance Connection Name
        "pg8000",
        user="user",
        password="password",
        db="db_name",
        ip_type= IPTypes.PUBLIC  # IPTypes.PRIVATE for private IP
    )
    return conn

engine = create_engine('postgresql+pg8000://', creator=getconn)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/api/process-file', methods=['POST'])
def process_file():
    data = json.loads(request.data.decode('utf-8'))
    # data = request.get_json()
    # print(data)
    old_filename = data['original']
    new_filename = data['nuevo']
    taskId = data['id_tarea']
    uploaded_file = os.path.join('/app/uploads', old_filename)
    processed_file = os.path.join('/app/uploads', new_filename)
    cmd = ['ffmpeg', '-i', uploaded_file,  processed_file]
    task = session.query(Tarea).filter_by(id=taskId).first()
    try:
        subprocess.run(cmd, check=True)
        print("Procesando tarea")
        task.estado = "processed"
        session.commit()
        return {}, 200
    except Exception as e:
        task.estado = "failed"
        session.commit()
        return {}, 500


if __name__ == '__main__':
    app.run()
