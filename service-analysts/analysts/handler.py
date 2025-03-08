import os
import jwt  # Asegúrate de tener instalado PyJWT
from utils.response import Response
from utils.serializable import serialize_document
from utils.model import User
from mongoengine import connect

# Configuración de variables de entorno (en producción se definen en el entorno Lambda)
DATABASE_URL = os.environ.get("DATABASE_URL")
JWT_SECRET = os.environ.get("JWT_SECRET", "supersecret")
MY_DATABASE_NAME = os.environ.get("MY_DATABASE_NAME", "vera-app")

# Conexión a MongoDB usando mongoengine
connect(MY_DATABASE_NAME, host=DATABASE_URL)


def handler_function(event, context):
    """
    Función Lambda para obtener analistas.

    Parámetros:
        event (dict): Objeto de evento que contiene la solicitud HTTP. Se espera:
                      - headers: Debe incluir "Authorization" con el token JWT (formato "Bearer <token>").
        context (object): Información del contexto de ejecución de Lambda.

    Retorna:
        dict: Respuesta HTTP en formato JSON.
              - Código 200: Retorna la lista de analistas.
              - Código 401: Si no se encuentra la sesión o el usuario no tiene rol ADMIN.
              - Código 404: Si no se encuentran analistas.
              - Código 500: Error interno del servidor.
    """
    try:
        # Extraer y validar el token JWT desde los headers
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(
                status_code=401,
                body={"error": "Authorization header missing or malformed"}
            ).to_dict()
        token = auth_header.split(" ", 1)[1]

        try:
            # Decodificar el token JWT
            session = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except Exception as e:
            return Response(
                status_code=401,
                body={"error": "Token inválido", "details": str(e)}
            ).to_dict()

        # Verificar que el usuario autenticado tenga rol "ADMIN"
        user = session.get("user", None)
        if not user:
            return Response(
                status_code=401,
                body={"error": "Unauthorized: se requiere user"}
            ).to_dict()

        if user.get("role") != "ADMIN":
            return Response(
                status_code=401,
                body={"error": "Unauthorized: se requiere rol ADMIN"}
            ).to_dict()

        evaluatorId = user.get("evaluatorId")
        if not evaluatorId:
            return Response(
                status_code=400,
                body={"error": "Evaluator ID no encontrado en la sesión"}
            ).to_dict()

        # Consultar los usuarios con rol "ANALYST" y el evaluatorId correspondiente
        analysts = User.objects(role="ANALYST", evaluatorId=evaluatorId)

        if not analysts:
            return Response(
                status_code=404,
                body={"error": "Analyst not found"}
            ).to_dict()

        # Convertir los resultados a formato serializable
        analysts_serializer = serialize_document(analysts)
        analysts_serializer = [serialize_document(analyst) for analyst in analysts_serializer]
        for analyst in analysts_serializer:
            del analyst["password"]

        return Response(
            status_code=200,
            body={"analysts": analysts_serializer}
        ).to_dict()

    except Exception as e:
        return Response(
            status_code=500,
            body={"error": "Internal server error", "details": str(e)}
        ).to_dict()


# Bloque de prueba local
if __name__ == "__main__":
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiNjc5ZDA1MDhjNDM0ZDdjMmM5M2IzYTBkIiwidXNlcm5hbWUiOiJyYm9uaWZheiIsInJvbGUiOiJBRE1JTiIsImV2YWx1YXRvcklkIjoiNjc5ZDA0ZDJjNDM0ZDdjMmM5M2IzYTA5IiwiZW1haWwiOiJyb2RyaWdvQHZhbGUucGUifSwiZXhwIjoxNzQ0MDA3MjIxfQ.UqmXGkGzftOL8UIXH656gqvnLak43U-Okdh1HoMMxns"
    test_headers = {
        "Authorization": f"Bearer {test_token}"
    }

    # Simular un evento para la función Lambda
    # En este caso, solo necesitamos headers ya que es una operación GET sin body
    event_test = {
        "headers": test_headers
    }

    # Ejecutar la función Lambda de prueba
    response = handler_function(event_test, {})
    print("Respuesta de la función Lambda:")
    print(response)
