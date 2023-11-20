import os
import subprocess
import time
import json
from modelos import Tarea
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector, IPTypes
from google.cloud import pubsub_v1

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

def process_file(old_filename, new_filename, taskId):
    uploaded_file = os.path.join('/home/giancarlo_corredor/bucket', old_filename)
    processed_file = os.path.join('/home/giancarlo_corredor/bucket', new_filename)
    cmd = ['ffmpeg', '-i', uploaded_file,  processed_file]
    task = session.query(Tarea).filter_by(id=taskId).first()
    try:
        subprocess.run(cmd, check=True)
        print("Procesando tarea")
        task.estado = "processed"
        session.commit()
        return True
    except Exception as e:
        task.estado = "failed"
        session.commit()
        return str(e)


project = "misw4204-202315-grupo21"
subscription = "conversor-sub"

subs = pubsub_v1.SubscriberClient()
subpath = subs.subscription_path(project, subscription)

while True:
    res = subs.pull(subscription=subpath, max_messages=1, return_immediately=True)

    if res.received_messages:
        message = res.received_messages[0].message.data
        subs.acknowledge(subscription=subpath, ack_ids=[res.received_messages[0].ack_id])
        # print(message)
        data = json.loads(message.decode('utf-8'))
        process_file(data['original'], data['nuevo'], data['id_tarea'])
    else:
        print("Nada nuevo")

    time.sleep(10)
