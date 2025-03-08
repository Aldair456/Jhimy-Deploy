import json
import os
import jwt  # Importar PyJWT
from mongoengine import connect
from utils.model import FinancialStatement, FinancialDatapoint
from utils.response import Response
from bson import ObjectId

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "supersecret")  # Se recomienda usar variables de entorno


def lambda_handler(event, context):
    try:
        # Conectar a la base de datos
        connect(db=os.environ['MY_DATABASE_NAME'], host=os.environ['DATABASE_URL'])

        # Obtener el ID del estado financiero desde los parámetros de la URL
        statement_id = event.get("pathParameters", {}).get("id")
        if not statement_id or not ObjectId.is_valid(statement_id):
            return Response(status_code=400, body={"error": "ID inválido"}).to_dict()

        # Verificar autorización con el Bearer Token
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "No autorizado"}).to_dict()

        token = auth_header.split(" ")[1]
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response(status_code=401, body={"error": "Token expirado"}).to_dict()
        except jwt.InvalidTokenError:
            return Response(status_code=401, body={"error": "Token inválido"}).to_dict()

        # Buscar el estado financiero
        statement = FinancialStatement.objects(id=ObjectId(statement_id)).first()
        if not statement:
            return Response(status_code=404, body={"error": "Estado financiero no encontrado"}).to_dict()

        # Eliminar todos los datapoints relacionados
        FinancialDatapoint.objects(financialStatementId=ObjectId(statement_id)).delete()

        # Eliminar el estado financiero
        statement.delete()

        return Response(status_code=200,
                        body={"success": True, "message": "Estado financiero eliminado correctamente"}).to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error interno", "details": str(e)}).to_dict()


if __name__ == "__main__":
    # Simulación de prueba local
    test_event = {
        "pathParameters": {"id": "67cc57a238d640b67c1b9d54"},
        "headers": {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiNjc5ZDA1MDhjNDM0ZDdjMmM5M2IzYTBkIiwidXNlcm5hbWUiOiJyYm9uaWZheiIsInJvbGUiOiJBRE1JTiIsImV2YWx1YXRvcklkIjoiNjc5ZDA0ZDJjNDM0ZDdjMmM5M2IzYTA5IiwiZW1haWwiOiJyb2RyaWdvQHZhbGUucGUifSwiZXhwIjoxNzQ0MDQyOTk0fQ.6PyKgQOIRMoPrBVmbwSGo_8D56al2HesA3NXjg-_J-I"}
    }
    print(lambda_handler(test_event, None))
