import json
import os
from bson import ObjectId
import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-financial-statements")
from utils.model import FinancialStatement  # Asegúrate de importar el modelo correcto
from utils.response import Response  # Importa la clase Response
from utils.serializable import serialize_document

"""""

 Autenticación con un Bearer Token
Extrae el id del negocio desde la URL
 Busca todos los estados financieros asociados al negocio en MongoDB
 Convierte los estados financieros en JSON
 Maneja errores con respuestas estructuradas
"""
def lambda_handler(event, context):
    try:
        # Verificar autorización con el Bearer Token
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "No autorizado"}).to_dict()

        # Obtener ID del negocio desde la URL
        business_id = event.get("pathParameters", {}).get("id")
        if not business_id or not ObjectId.is_valid(business_id):
            return Response(status_code=400, body={"error": "ID de negocio inválido"}).to_dict()

        # Buscar estados financieros asociados al negocio
        statements = FinancialStatement.objects(businessId=ObjectId(business_id))

        # Serializar los estados financieros
        serialized_statements = [serialize_document(statement.to_mongo().to_dict()) for statement in statements]


        return Response(status_code=200, body=serialized_statements).to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error interno", "details": str(e)}).to_dict()
# correguir solo el guradado en donde debe de guardarse porque lo saca del staement

if __name__ == "__main__":
    test_event = {
        "headers": {"Authorization": "Bearer test_token"},
        "pathParameters": {"id": "679d086b1d4641c193691300"}
    }
    print(lambda_handler(test_event, None))
