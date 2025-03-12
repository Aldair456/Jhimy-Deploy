import json
import os
from mongoengine import connect
from bson import ObjectId
import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-financial-statements")
from utils.model import FinancialStatement,  FinancialDatapoint, Account
from utils.response import Response
from utils.serializable import serialize_document
""""
Se conecta a MongoDB.
Verifica si la petición tiene un token válido.
Obtiene los datos (ID del negocio, tipo de estado financiero, años y valores).
Crea el estado financiero si no existe.
Guarda los datos de cada cuenta financiera con sus valores y detalles.
Retorna un JSON con el estado financiero guardado.
"""

#falta probar
def lambda_handler(event, context):
    try:
        connect(db=os.environ['MY_DATABASE_NAME'], host=os.environ['DATABASE_URL'])

        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "No autorizado"}).to_dict()

        body = json.loads(event.get("body", "{}"))
        business_id = body.get("businessId")
        statement_type = body.get("type")
        years = body.get("years", [])
        data = body.get("data", {})

        if not business_id or not statement_type or not years:
            return Response(status_code=400, body={"error": "Faltan datos requeridos (businessId, type, o years)"}).to_dict()

        year_objects = []
        for year in years:
          year_obj = Year.objects(year=year).first()
          if not year_obj:
           year_obj = Year(year=year)
           year_obj.save()
           year_objects.append(year_obj)
  
        statement = FinancialStatement(
            businessId=business_id,
            type=statement_type,
            years=year_objects
        )
        statement.save()

        datapoints = []
        for account_id, year_values in data.items():
            account = Account.objects(id=ObjectId(account_id)).first()
            if not account:
                continue

            for year in years:
                year_obj = next((y for y in year_objects if y.year == year), None)
                if not year_obj:
                    continue

                value = year_values.get("value", 0)
                details = [
                    {"name": detail["itemName"], "value": detail["yearValues"].get(str(year), 0)}
                    for detail in year_values.get("details", [])
                ]

                datapoint = FinancialDatapoint(
                    businessId=business_id,
                    value=value,
                    details=details,
                    account=account,
                    year=year_obj,
                    financialStatement=statement
                )
                datapoints.append(datapoint)

        if datapoints:
            FinancialDatapoint.objects.insert(datapoints)
        response = Response(status_code=201, body=serialize_document(statement.to_mongo().to_dict()))
 
        return response.to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error interno", "details": str(e)}).to_dict()



if __name__ == "__main__":
    test_event = {
        "headers": {"Authorization": "Bearer test_token"},
        "body": json.dumps({
            "businessId": "67c76aa2c0f88e26ec2fba16",# se tiene que pasar un bussines ID para crear el staments 
            "type": "official",
            "years": [2023, 2024],
            "data": {
                "65f0c7e45d3b2a7f30e92a12": {
                    "value": 10000,
                    "details": [
                        {"itemName": "Efectivo", "yearValues": {"2023": 5000, "2024": 5000}}
                    ]
                }
            }
        })
    }

    print(lambda_handler(test_event, None))
