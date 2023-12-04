# MISW4204-2023-15 Grupo #21

# Requisitos
- gcloud CLI
- Cuenta de servicio de GCP con roles que permitan interactuar con Cloud Storage, Pub/Sub, y Cloud SQL.
- Instancia de Cloud SQL
- Tema en pub/sub
- Bucket en Cloud Storage

# Instrucciones para desplegar los servicios a Cloud Run

1. Autorizar la cuenta de usuario de GCP
```
$ gcloud auth application-default login
```

2. Creamos y descargamos una clave de la cuenta de servicio que vamos a usar. El archivo con la clave debe llamarse 'credenciales.json', y debe estar localizado en la raíz de este repositorio.

3. Renombramos el archivo 'Dockerfile.app' a 'Dockerfile'.

4. Ejecutamos el siguiente comando para desplegar la API.
```
gcloud run deploy misw-4204-202315-21-api --source . --execution-environment gen2 --allow-unauthenticated --port 8000 --cpu 2 --memory 4Gi
```

5. Devolvemos los cambios del paso 3, renombrando el archivo 'Dockerfile' como 'Dockerfile.app'. Luego renombramos el archivo 'Dockerfile.worker' a 'Dockerfile'.

6. Ejecutamos el siguiente comando para desplegar el worker o batch.
```
gcloud run deploy misw-4204-202315-21-worker --source . --execution-environment gen2 --allow-unauthenticated --port 8000 --cpu 4 --memory 16Gi
```
