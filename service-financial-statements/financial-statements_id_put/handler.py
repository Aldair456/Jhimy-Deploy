import json
from bson import ObjectId
from datetime import datetime
import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-financial-statements")
from utils.model import FinancialStatement, FinancialDatapoint  # Asegúrate de importar los modelos correctos
from utils.response import Response  # Importa la clase Response
from utils.serializable import serialize_document

#falta
def lambda_handler(event, context):
    try:
        # Verificar autorización con el Bearer Token
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "No autorizado"}).to_dict()

        # Obtener datos de la solicitud
        body = json.loads(event.get("body", "{}"))
        statementId = event.get("pathParameters", {}).get("id")
        if not statementId or not ObjectId.is_valid(statementId):
            return Response(status_code=400, body={"error": "ID inválido"}).to_dict()

        businessId = body.get("businessId")
        years = body.get("years", [])
        data = body.get("data", {})
        currency = body.get("currency")
        scale = body.get("scale")

        if not businessId or not years or not isinstance(years, list) or not years:
            return Response(status_code=400, body={"error": "Faltan datos requeridos (businessId, years)"}).to_dict()

        # Buscar y actualizar el estado financiero
        statement = FinancialStatement.objects(id=ObjectId(statementId)).first()
        if not statement:
            return Response(status_code=404, body={"error": "Estado financiero no encontrado"}).to_dict()

        statement.currency = currency
        statement.scaleType = scale
        statement.updatedAt = datetime.utcnow()
        statement.save()

        # Obtener o crear años como objetos en una lista de diccionarios
        yearRecords = [{"year": year} for year in years]

        # Eliminar datapoints existentes
        FinancialDatapoint.objects(financialStatement=statement).delete()

        # Crear nuevos datapoints
        datapoints = []
        for accountId, yearValues in data.items():
            for year in years:
                yearRecord = next((yr for yr in yearRecords if yr["year"] == year), None)
                if not yearRecord:
                    continue

                yearData = yearValues.get(year)
                if yearData:
                    details = yearData.get("details", [])
                    datapoints.append(FinancialDatapoint(
                        businessId=businessId,
                        value=yearData.get("value", 0),
                        details=details,
                        accountId=accountId,
                        year=yearRecord["year"],
                        financialStatement=statement
                    ))

        if datapoints:
            FinancialDatapoint.objects.insert(datapoints)

        return Response(status_code=200, body=serialize_document(statement.to_mongo().to_dict())).to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error interno", "details": str(e)}).to_dict()


if __name__ == "__main__":
    test_event = {
        "headers": {"Authorization": "Bearer test_token"},
        "pathParameters": {"id": "67cf61d6b66c8bdbc2993c4b"},
        "body": json.dumps({
            "businessId": "12345",
            "currency": "USD",
            "scale": "millions",
            "years": [2023, 2024],
            "data": {"account1": {2023: {"value": 1000, "details": [{"name": "Item A", "value": 500}]}}}
        })
    }
    print(lambda_handler(test_event, None))