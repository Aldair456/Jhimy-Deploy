import os
import json
import jwt  # pip install PyJWT
from mongoengine import connect, DoesNotExist
from utils.response import Response
from utils.serializable import serialize_document
from utils.model import User,Deal,Business
from bson import ObjectId
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")


def lambda_handler(event, context):
    """
    Función Lambda para obtener la información del usuario autenticado y sus relaciones.

    Se espera que la solicitud incluya un header "Authorization" en el formato "Bearer <token>".
    El token JWT debe contener un objeto "user" con al menos las propiedades "email", "id", "role" y "evaluatorId".

    Retorna:
      - 200: Con el objeto del usuario (y, en caso de ADMIN, sus relaciones).
      - 401: Si no está autenticado.
      - 404: Si no se encuentra el usuario.
      - 500: En caso de error interno.
    """
    try:
        # Extraer y decodificar el token JWT desde el header "Authorization"
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(
                status_code=401,
                body={"error": "Not authenticated"}
            ).to_dict()

        token = auth_header.split(" ", 1)[1]
        try:
            session = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except Exception as e:
            return Response(
                status_code=401,
                body={"error": "Not authenticated", "details": str(e)}
            ).to_dict()

        user_session = session.get("user", {})
        if not user_session.get("email"):
            return Response(
                status_code=401,
                body={"error": "Not authenticated"}
            ).to_dict()

        user_id = user_session.get("id")
        evaluator_id = user_session.get("evaluatorId")
        role = user_session.get("role")

        if role == "ADMIN":
            try:
                # Buscar usuario con solo los campos necesarios
                user = User.objects.get(id=ObjectId(user_id))
                user = serialize_document(user)
                # Buscar analistas asociados al mismo `evaluatorId`
                analysts = User.objects(role="ANALYST", evaluatorId=ObjectId(evaluator_id))
                analysts = [serialize_document(analyst) for analyst in analysts]
                businesses = Business.objects( id=ObjectId(evaluator_id))
                businesses = [serialize_document(business) for business in businesses]
                deals = Deal.objects(id=ObjectId(evaluator_id))
                deals = [serialize_document(deal) for deal in deals]

                # Aquí podrías agregar las consultas de `businesses` y `deals` si los modelos existen en MongoEngine

                user_response = {
                    **user,
                    "allAnalysts": analysts,
                    "allBusinesses": businesses,  # Reemplazar con datos reales
                    "allDeals": deals  # Reemplazar con datos reales
                }

                return Response(
                    status_code=200,
                    body=user_response
                ).to_dict()
            except DoesNotExist:
                return Response(
                    status_code=404,
                    body={"error": "User not found"}
                ).to_dict()

        else:
            try:
                user = User.objects.get(id=ObjectId(user_id))
                user_response = serialize_document(user)
                return Response(
                    status_code=200,
                    body=user_response
                ).to_dict()
            except DoesNotExist:
                return Response(
                    status_code=404,
                    body={"error": "User not found"}
                ).to_dict()

    except Exception as e:
        print("Error in GET /api/user:", str(e))
        return Response(
            status_code=500,
            body={"error": "Internal server error", "details": str(e)}
        ).to_dict()


# Bloque opcional para pruebas locales
if __name__ == "__main__":
    # Simulación de un token JWT para un usuario ADMIN
    # (Nota: Debes generar el token con la clave secreta correcta y con un payload similar)

    admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiNjc5ZDA1MDhjNDM0ZDdjMmM5M2IzYTBkIiwidXNlcm5hbWUiOiJyYm9uaWZheiIsInJvbGUiOiJBRE1JTiIsImV2YWx1YXRvcklkIjoiNjc5ZDA0ZDJjNDM0ZDdjMmM5M2IzYTA5IiwiZW1haWwiOiJyb2RyaWdvQHZhbGUucGUifSwiZXhwIjoxNzQzOTc5ODUxfQ.Rhn2S2GyJREDRlXKfSQc9RWS4tz5PvAUeIV2lDIlbj4"
    test_event = {
        "httpMethod": "GET",
        "headers": {
            "Authorization": f"Bearer {admin_token}"
        }
    }
    response = lambda_handler(test_event, {})
    print("Response from GET lambda:", response)
