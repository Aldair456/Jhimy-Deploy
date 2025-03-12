import json
from mongoengine import connect
from bson import ObjectId
import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-eeff")
from utils.model import FinancialDatapoint, Account  # Modelos en MongoEngine
from utils.response import Response  # Clase Response para respuestas formateadas
from utils.serializable import serialize_document


""""
businessId se pasa en la URL de la solicitud. La función responde con los datos financieros de ese negocio,
 siempre y cuando la autenticación sea correcta y el businessId sea válido.
"""
def lambda_handler(event, context):
    try:
        # Verificar autorización con el Bearer Token
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "No autorizado"}).to_dict()

        # Obtener `businessId` desde los parámetros de la URL
        path_params = event.get("pathParameters", {})
        business_id = path_params.get("businessId")
        if not business_id or not ObjectId.is_valid(business_id):
            return Response(status_code=400, body={"error": "ID de negocio inválido"}).to_dict()

        # Obtener los datos financieros asociados al `businessId`
        financial_data = FinancialDatapoint.objects(businessId=ObjectId(business_id))
        # Incluir información de la cuenta relacionada
        serialized_data = [serialize_document(data.to_mongo().to_dict()) for data in financial_data]
        return Response(status_code=200, body=serialized_data).to_dict()

    except Exception as e:
        return Response(status_code=500,
                        body={"error": "Error al obtener datos financieros", "details": str(e)}).to_dict()


if __name__ == "__main__":
    # Simulación de prueba local
    test_event = {
        "headers": {"Authorization": "Bearer test_token"},
        "pathParameters": {"businessId": "67802e0a80547b162bf07dd0"}
    }
    print(lambda_handler(test_event, None))
