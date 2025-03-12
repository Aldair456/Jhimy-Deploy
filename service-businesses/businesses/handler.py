import os
import json
import sys

sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-businesses")

import utils
from utils.response import Response
from utils.model import Business
from utils.serializable import serialize_document

def handler(event, context):
    """
    Lambda function para obtener los negocios asociados a un evaluador.
    Se espera que event["queryStringParameters"]["evaluatorId"] contenga el ID del evaluador.
    """
    try:
        query_params = event.get("queryStringParameters", {})
        evaluator_id = query_params.get("evaluatorId")

        if not evaluator_id:
            return Response(
                status_code=400,
                body={"error": "Falta el parámetro 'evaluatorId'"}
            ).to_dict()

        # Obtener los negocios usando el ORM
        #   si deseas   mas datos quitar el .only , <-
        businesses = Business.objects(evaluatorId=evaluator_id).only("id", "ruc", "razonSocial", "createdAt")

        # Convertir a JSON
        business_list = [serialize_document(business.to_mongo().to_dict()) for business in businesses]

        return Response(
            status_code=200,
            body={"data": business_list}
        ).to_dict()

    except Exception as e:
        return Response(
            status_code=500,
            body={"error": "Error al obtener negocios", "details": str(e)}
        ).to_dict()

if __name__ == "__main__":
    event = {
        "queryStringParameters": {
            "evaluatorId": "677ea035c434d7c2c93b39a1"
        }
    }
    print(handler(event=event, context={}))
