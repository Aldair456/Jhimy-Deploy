from bson import ObjectId

import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-financial-statements")
from utils.model import FinancialStatement, FinancialDatapoint  # Asegúrate de importar los modelos correctos
from utils.response import Response  # Importa la clase Response
from utils.serializable import serialize_document

# testeado 
def lambda_handler(event, context):
    try:
        # Verificar autorización con el Bearer Token
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "No autorizado"}).to_dict()

        # Obtener ID del estado financiero desde la URL
        statementId = event.get("pathParameters", {}).get("id")
        if not statementId or not ObjectId.is_valid(statementId):
            return Response(status_code=400, body={"error": "ID inválido"}).to_dict()

        # Buscar el estado financiero en la base de datos
        statement = FinancialStatement.objects(id=ObjectId(statementId)).first()
        if not statement:
            return Response(status_code=404, body={"error": "Estado financiero no encontrado"}).to_dict()

        # Obtener los datapoints y organizarlos por año
        datapoints = FinancialDatapoint.objects(financialStatement=statement)
        datapoints_by_year = {}
        for dp in datapoints:
            year = dp.year
            if year not in datapoints_by_year:
                datapoints_by_year[year] = []
            datapoints_by_year[year].append({
                "id": str(dp.id),
                "value": dp.value,
                "details": dp.details,
                "year": dp.year,
                "accountId": dp.accountId
            })

        response_body = {
            **serialize_document(statement.to_mongo().to_dict()),
            "datapointsByYear": datapoints_by_year
        }

        return Response(status_code=200, body=response_body).to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error interno", "details": str(e)}).to_dict()


if __name__ == "__main__":
    test_event = {
        "headers": {"Authorization": "Bearer test_token"},
        "pathParameters": {"id": "67cf66d10fc38d9c1dc0915b"}
    }
    print(lambda_handler(test_event, None))
