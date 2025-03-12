import os
import json
from mongoengine import connect
import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-businesses")
from utils.response import Response
from utils.model import (Business)  # Importa el modelo ORM
from utils.serializable import serialize_document


def handler(event, context):
    """
    Lambda function para actualizar un negocio por su ID.
    Se espera:
    - event["pathParameters"]["businessId"]: ID del negocio a actualizar.
    - event["body"]: JSON con los campos a modificar.
    """
    try:
        path_params = event.get("pathParameters", {})
        business_id = path_params.get("businessId")

        if not business_id:
            return Response(
                status_code=400,
                body={"error": "Falta el parámetro 'businessId'"}
            ).to_dict()

        body = event.get("body")
        if not body:
            return Response(
                status_code=400,
                body={"error": "Falta el cuerpo de la solicitud"}
            ).to_dict()

        # Convertir body de string a dict si es necesario
        if isinstance(body, str):
            body = json.loads(body)

        # Buscar y actualizar el negocio
        business = Business.objects(id=business_id).first()
        if not business:
            return Response(
                status_code=404,
                body={"error": "Negocio no encontrado"}
            ).to_dict()

        # Actualizar los campos dinámicamente
        business.modify(**body)
        business.save()

        # Convertir a JSON
        business_data = serialize_document(business.to_mongo().to_dict())

        return Response(
            status_code=200,
            body=business_data
        ).to_dict()

    except Exception as e:
        return Response(
            status_code=500,
            body={"error": "Error al actualizar negocio", "details": str(e)}
        ).to_dict()

if __name__ == "__main__":
    event = {
        "pathParameters": {
            "businessId": "6786e21b6106b8b2141497fd"
        },
        "body": json.dumps({"ruc": "123", "razonSocial": "Nueva Empresa SAC"})
    }
    print(handler(event=event, context={}))
