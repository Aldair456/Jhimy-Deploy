import os
import json
import datetime
import jwt  # PyJWT para manejar JWT
from mongoengine import DoesNotExist
from utils.response import Response
from utils.model import User,Evaluator
from utils.serializable import serialize_document
from bson import ObjectId
# Clave secreta para JWT
SECRET_KEY = os.environ.get("JWT_SECRET", "supersecret")


def handler_function(event, context):
    """
    Lambda para crear un usuario ANALYST en MongoDB.

    Parámetros:
    - event (dict): Contiene headers (Authorization) y body con los datos del usuario.
    - context: Información del entorno de ejecución (no se usa en esta función).

    Retorna:
    - dict: Respuesta HTTP con código y mensaje.
    """
    try:
        # 1️⃣ Extraer y validar el token de la cabecera Authorization
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return Response(401, {"error": "Authorization header missing or malformed"}).to_dict()

        token = auth_header.split(" ", 1)[1]

        try:
            session = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response(401, {"error": "Token expirado"}).to_dict()
        except jwt.InvalidTokenError:
            return Response(401, {"error": "Token inválido"}).to_dict()

        # 2️⃣ Verificar si el usuario es ADMIN
        user = session.get("user", None)
        if not user:
            return Response(
                status_code=401,
                body={"error": "Unauthorized: se requiere user"}
            ).to_dict()
        if user.get("role") != "ADMIN":
            return Response(401, {"error": "Unauthorized: se requiere rol ADMIN"}).to_dict()

        evaluatorId = user.get("evaluatorId")
        if not evaluatorId:
            return Response(400, {"error": "Evaluator ID no encontrado en la sesión"}).to_dict()

        # 3️⃣ Extraer y validar los datos del cuerpo (body)
        body = event.get("body")
        if not body:
            return Response(400, {"error": "Falta el cuerpo de la solicitud"}).to_dict()

        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return Response(400, {"error": "El cuerpo no es un JSON válido"}).to_dict()

        required_fields = ["username", "password", "name", "email"]
        missing_fields = [field for field in required_fields if not body.get(field)]

        if missing_fields:
            return Response(
                400, {"error": f"Los siguientes campos son requeridos: {', '.join(missing_fields)}"}
            ).to_dict()

        username = body["username"]
        password = body["password"]
        name = body["name"]
        email = body["email"]

        # 4️⃣ Verificar si el usuario ya existe
        if User.objects(username=username).first():
            return Response(409, {"error": "El usuario ya existe"}).to_dict()

        # 5️⃣ Crear el usuario en la base de datos
        evaluator_instance = Evaluator.objects.get(id=ObjectId(evaluatorId))
        print(evaluator_instance)
        new_user = User(
            username=username,
            password=password,  # 🔴 IMPORTANTE: En producción, hashear la contraseña
            role="ANALYST",
            evaluatorId=evaluator_instance,
            name=name,
            email=email,
            createdAt=datetime.datetime.utcnow(),
            updatedAt=datetime.datetime.utcnow(),
        )
        new_user.save()

        # 6️⃣ Retornar el usuario creado (sin la contraseña)
        user_data = new_user.to_mongo().to_dict()
        user_data.pop("password", None)  # No devolver la contraseña en la respuesta

        return Response(200, {"data": serialize_document(user_data)}).to_dict()

    except Exception as e:
        return Response(500, {"error": "Error interno del servidor", "details": str(e)}).to_dict()


# Bloque opcional para pruebas locales
if __name__ == "__main__":
    # Simular headers con un token JWT para un usuario ADMIN
    # En este ejemplo, generamos un token para pruebas (valido por 30 días)

    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiNjc5ZDA1MDhjNDM0ZDdjMmM5M2IzYTBkIiwidXNlcm5hbWUiOiJyYm9uaWZheiIsInJvbGUiOiJBRE1JTiIsImV2YWx1YXRvcklkIjoiRXZhbHVhdG9yIG9iamVjdCIsImVtYWlsIjoicm9kcmlnb0B2YWxlLnBlIn0sImV4cCI6MTc0NDAxMDYzMn0.hctVW2YJLwZJfbfEO0032UBTD7KIH1o6gMRoYvijXiE"
    test_headers = {
        "Authorization": f"Bearer {test_token}"
    }

    # Simular un body de solicitud para crear un analista
    test_body = {
        "username": "analystUser13",
        "password": "analystPassword",
        "name": "Analyst Name",
        "email": "analyst@example.com"
    }

    # Evento de prueba
    event_test = {
        "headers": test_headers,
        "body": json.dumps(test_body)
    }

    # Ejecutar la función Lambda de prueba
    response = handler_function(event_test, {})
    print("Respuesta de la función Lambda:")
    print(response)
