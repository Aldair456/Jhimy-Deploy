import json
from mongoengine import connect
import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-eeff")
from utils.model import Account  # Modelo de la colección "Account"

from utils.response import Response  # Clase Response para formatear respuestas
from utils.serializable import serialize_document
""""

Este código es una función Lambda que se conecta a una base de datos MongoDB, obtiene todas las cuentas de la colección Account, las serializa y devuelve los resultados como una respuesta formateada en JSON. Aquí te explico qué hace cada parte del código:

"""

def lambda_handler(event, context):
    try:
        # Verificar autorización con el Bearer Token
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "No autorizado"}).to_dict()

        # Obtener todas las cuentas de la base de datos
        accounts = Account.objects()

        # Serializar los resultados
        serialized_accounts = [serialize_document(account.to_mongo().to_dict()) for account in accounts]

        return Response(status_code=200, body=serialized_accounts).to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error interno", "details": str(e)}).to_dict()


if __name__ == "__main__":
    # Simulación de prueba local
    test_event = {
        "headers": {"Authorization": "Bearer test_token"}
    }
    print(lambda_handler(test_event, None))