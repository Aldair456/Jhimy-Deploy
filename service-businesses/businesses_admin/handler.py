import json
import os
import jwt  # PyJWT para decodificar el token JWT
from mongoengine import connect
import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-businesses")

from utils.model import Business  # Asegúrate de importar el modelo correcto
from utils.response import Response  # Importa la clase Response

# Clave secreta para decodificar el token (debe ser la misma usada para generarlo)
SECRET_KEY = os.environ.get("JWT_SECRET", "supersecret")

def lambda_handler(event, context):
    try:
        # Conectar a la base de datos
        connect(db=os.environ['MY_DATABASE_NAME'], host=os.environ['DATABASE_URL'])

        # Obtener el token de autorización
        auth_header = event.get("headers", {}).get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "Token no proporcionado o inválido"}).to_dict()

        token = auth_header.split(" ")[1]  # Extraer el token real

        try:
            # Decodificar el token
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response(status_code=401, body={"error": "Token expirado"}).to_dict()
        except jwt.InvalidTokenError:
            return Response(status_code=401, body={"error": "Token inválido"}).to_dict()

        user = payload.get("user")
        if not user:
            return Response(status_code=400, body={"error": "user not found"}).to_dict()

        evaluator_id = user.get("evaluatorId")
        if not evaluator_id:
            return Response(status_code=401, body={"error": "No autorizado"}).to_dict()

        # Buscar los negocios asociados al evaluatorId
        # Usamos solo "id" y "analistaIds" en la proyección para evitar el error.
        businesses = Business.objects(evaluatorId=evaluator_id).only("id", "analistaIds").select_related()

        # Construir la lista de negocios
        business_list = [
            {
                "id": str(b.id),
                "analistas": [{"id": str(a)} for a in b.analistaIds]
            }
            for b in businesses
        ]

        return Response(status_code=200, body=business_list).to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error al cargar los negocios", "details": str(e)}).to_dict()


if __name__ == "__main__":
    # Simulación de prueba local con un token de ejemplo
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiNjc5ZDA1MDhjNDM0ZDdjMmM5M2IzYTBkIiwidXNlcm5hbWUiOiJyYm9uaWZheiIsInJvbGUiOiJBRE1JTiIsImV2YWx1YXRvcklkIjoiNjc5ZDA0ZDJjNDM0ZDdjMmM5M2IzYTA5IiwiZW1haWwiOiJyb2RyaWdvQHZhbGUucGUifSwiZXhwIjoxNzQ0MDQyNDEzfQ.ttH_l9piZuCif4IK8vwIiE-AFllqJ4ar8-QA4XYEVMs"

    test_event = {
        "headers": {"Authorization": f"Bearer {test_token}"}
    }
    print(lambda_handler(test_event, None))
