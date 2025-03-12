import json
from mongoengine import connect
from bson import ObjectId
import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-eeff")
from utils.model import FinancialDatapoint  # Importar modelo de MongoEngine
from utils.response import Response  # Clase Response para respuestas formateadas
""""
actualizar datos financieros de un negocio basado en un businessId. Te explico paso a paso qué hace el código:"
"""
#falta probar

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

        # Obtener los datos enviados en el cuerpo de la solicitud
        body = json.loads(event.get("body", "{}"))
        value = body.get("value")
        if value is None:
            return Response(status_code=400, body={"error": "Valor faltante"}).to_dict()

        # Buscar y actualizar el dato financiero
        financial_data = FinancialDatapoint.objects(businessId=ObjectId(business_id)).first()
        if not financial_data:
            return Response(status_code=404, body={"error": "Dato financiero no encontrado"}).to_dict()

        financial_data.update(value=value)
        print(financial_data)
        financial_data.save()

        return Response(status_code=200, body={"message": "Datos actualizados correctamente"}).to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error al actualizar datos financieros", "details": str(e)}).to_dict()


if __name__ == "__main__":
    # Simulación de prueba local
    test_event = {
        "headers": {"Authorization": "Bearer test_token"},
        "pathParameters": {"businessId": "67cf41b44aec96628112f65a"},
        "body": json.dumps({"value": 9010})
    }
    print(lambda_handler(test_event, None))
