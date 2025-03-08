import json
import os
from bson import ObjectId
from utils.model import FinancialStatement  # Asegúrate de importar el modelo correcto
from utils.response import Response  # Importa la clase Response
from utils.serializable import serialize_document

def lambda_handler(event, context):
    try:
        # Conectar a la base de datos

        # Verificar autorización con el Bearer Token
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "No autorizado"}).to_dict()

        # Obtener el ID del estado financiero desde los parámetros de la URL
        path_params = event.get("pathParameters", {})
        statement_id = path_params.get("id")
        if not statement_id or not ObjectId.is_valid(statement_id):
            return Response(status_code=400, body={"error": "ID inválido"}).to_dict()
        # Buscar el estado financiero
        statement = FinancialStatement.objects(id=ObjectId(statement_id)).first()

        if not statement:
            return Response(status_code=404, body={"error": "Estado financiero no encontrado"}).to_dict()

        return Response(status_code=200, body=serialize_document(statement.to_mongo().to_dict())).to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error interno", "details": str(e)}).to_dict()


if __name__ == "__main__":
    # Simulación de prueba local
    test_event = {
        "headers": {"Authorization": "Bearer test_token"},
        "pathParameters": {"id": "67c1ebe6f2c06183ea1f7743"},
        "httpMethod": "GET"
    }
    print(lambda_handler(test_event, None))
