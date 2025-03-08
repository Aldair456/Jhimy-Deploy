import json
from mongoengine import connect
from utils.model import FinancialDatapoint  # Modelo en MongoEngine
from utils.response import Response  # Clase Response para formatear respuestas

##falta probar
def lambda_handler(event, context):
    try:
        # Verificar autorización con el Bearer Token
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "No autorizado"}).to_dict()

        # Leer el cuerpo de la solicitud
        body = json.loads(event.get("body", "{}"))
        business_id = body.get("businessId")
        data = body.get("data", [])

        if not business_id or not data:
            return Response(status_code=400, body={"error": "Faltan datos requeridos"}).to_dict()

        # Insertar los datos en la base de datos
        created_data = []
        for item in data:
            new_datapoint = FinancialDatapoint(
                **item,  # Agrega los datos del objeto
                businessId=business_id  # Asocia el businessId
            )
            new_datapoint.save()
            created_data.append(new_datapoint.to_mongo().to_dict())

        return Response(status_code=201, body=created_data).to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error interno del servidor", "details": str(e)}).to_dict()


if __name__ == "__main__":
    # Simulación de prueba local
    test_event = {
        "headers": {"Authorization": "Bearer test_token"},
        "body": json.dumps({
            "businessId": "67c1ebe6f2c06183ea1f7743",
            "data": [
                {"accountId": "6786a3467c262b8d3c1892c0", "amount": 1000, "category": "Ventas"},
                {"accountId": "6786a3467c262b8d3c1892c1", "amount": 500, "category": "Gastos"}
            ]
        })
    }
    print(lambda_handler(test_event, None))
