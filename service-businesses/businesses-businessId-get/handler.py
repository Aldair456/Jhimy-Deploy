import os
import json
from mongoengine import connect, disconnect
from utils.response import Response
from utils.model import Business  # Importa el modelo ORM
from utils.serializable import serialize_document

def handler(event, context):
    """
    Lambda function para obtener un negocio por su ID.
    Se espera que event["pathParameters"]["businessId"] contenga el ID del negocio.
    """
    try:
        path_params = event.get("pathParameters", {})
        business_id = path_params.get("businessId")

        if not business_id:
            return Response(
                status_code=400,
                body={"error": "Falta el parámetro 'businessId'"}
            ).to_dict()

        # Obtener el negocio usando el ORM
        business = Business.objects(id=business_id).first()

        if not business:
            return Response(
                status_code=404,
                body={"error": "Negocio no encontrado"}
            ).to_dict()

        # Convertir a JSON
        business_data = serialize_document(business.to_mongo().to_dict())

        return Response(
            status_code=200,
            body=business_data
        ).to_dict()

    except Exception as e:
        return Response(
            status_code=500,
            body={"error": "Error al obtener los datos del negocio", "details": str(e)}
        ).to_dict()

if __name__ == "__main__":
    event = {
        "pathParameters": {
            "businessId": "67802e0a80547b162bf07dd0"
        }
    }
    print(handler(event=event, context={}))