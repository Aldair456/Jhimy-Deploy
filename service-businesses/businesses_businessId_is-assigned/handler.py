import json
import os
import jwt
from mongoengine import connect
import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-businesses")

from utils.model import Business  # Asegúrate de importar el modelo correcto

# Usa el businessId para determinar si el usuario con ese test_token
# tiene acceso al business. Si lo tiene retorna true, en caso contrario false.
def decode_jwt_token(event):
    headers = event.get("headers", {})
    auth_header = headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    secret_key = os.environ.get("JWT_SECRET_KEY", "supersecret")

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def lambda_handler(event, context):
    # Conectar a la base de datos
    connect(db=os.environ['MY_DATABASE_NAME'], host=os.environ['DATABASE_URL'])

    # Obtener el businessId desde los parámetros de la URL
    business_id = event.get("pathParameters", {}).get("businessId")
    if not business_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Falta el businessId"})}

    # Obtener la sesión del usuario desde el Bearer Token
    session = decode_jwt_token(event)
    user = session.get("user") if session else None
    if not user or not user.get("id"):
        return {"statusCode": 401, "body": json.dumps({"error": "No autorizado"})}

    # Buscar el negocio en la base de datos
    business = Business.objects(id=business_id).first()
    if not business:
        return {"statusCode": 404, "body": json.dumps({"error": "Negocio no encontrado"})}

    # Verificar si el usuario está en la lista de analistas
    # Se convierte cada ObjectId a string directamente
    is_analyst = user["id"] in [str(a) for a in business.analistaIds]
    return {
        "statusCode": 200,
        "body": json.dumps({"isAnalyst": is_analyst})
    }

if __name__ == "__main__":
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiNjdjYmVkMWJkNzQzMTNhYjc0OTk2NDhjIiwidXNlcm5hbWUiOiJhbmFseXN0VXNlcjEwIiwicm9sZSI6IkFOQUxZU1QiLCJldmFsdWF0b3JJZCI6IkV2YWx1YXRvciBvYmplY3QiLCJlbWFpbCI6ImFuYWx5c3RAZXhhbXBsZS5jb20ifSwiZXhwIjoxNzQ0MDM4Nzg0fQ.G46Z-rMTcdN-S_8MxquSeuewxgePN4D840dfKZeeumA"
    test_headers = {
        "Authorization": f"Bearer {test_token}"
    }
    event = {
        "pathParameters": {
            "businessId": "67802e0a80547b162bf07dd0"
        },
        "headers": test_headers
    }
    print(lambda_handler(event=event, context={}))
