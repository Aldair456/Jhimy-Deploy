
#
import os
import sys

sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-analysts")

#

import os
import json
import datetime
import jwt  # pip install PyJWT
from mongoengine import connect
from utils.model import User  # Asegúrate de que este módulo esté en tu PYTHONPATH
from utils.serializable import serialize_document


os.environ['JWT_SECRET'] = "supersecret"


SECRET_KEY = os.environ.get("JWT_SECRET", "supersecret")

def lambda_handler(event, context):
    """
    Función Lambda para autenticación utilizando MongoEngine y JWT.

    Se espera que el body de la solicitud (JSON) contenga:
      - username: Nombre de usuario.
      - password: Contraseña (en texto plano; en producción se deben usar contraseñas hasheadas).

    Flujo:
      1. Valida que el body esté presente y sea un JSON.
      2. Busca al usuario en la colección "User" mediante el modelo de MongoEngine.
      3. Verifica que exista y que la contraseña coincida.
      4. Genera un token JWT que incluye id, username, role y evaluatorId.
      5. Retorna el token con un código 200 o errores apropiados (400, 401, 404, 500).
    """
    try:
        body = event.get("body")
        if not body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Falta el cuerpo de la solicitud"})
            }
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError as e:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "El cuerpo no es un JSON válido", "details": str(e)})
                }

        username = body.get("username")
        password = body.get("password")
        if not username or not password:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Se requieren 'username' y 'password'"})
            }

        # Buscar al usuario usando el modelo User de MongoEngine
        user = User.objects(username=username).first()

        if not user:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Usuario no encontrado"})
            }


        # Verificar la contraseña (en producción, usa contraseñas hasheadas)
        if user.password != password:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Contraseña inválida"})
            }

        # Preparar el payload para el token JWT

        user = serialize_document(user.to_mongo().to_dict())

        payload = {
            "user": {
                "id": user.get("_id"),
                "username": user.get("username"),
                "role":user.get("role"),
                "evaluatorId": user.get("evaluatorId"),
                "email": user.get("email")
            },
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Inicio de sesión exitoso",
                "token": token
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Error interno del servidor", "details": str(e)})
        }

# Bloque opcional para pruebas locales
if __name__ == "__main__":
    # Simulación de un evento HTTP con body JSON para autenticación
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "username": "juanp1",
            "password": "analystPassword"
        })
    }
    response = lambda_handler(test_event, {})
    print("Respuesta de la función Lambda:")
    print(response)
# checking