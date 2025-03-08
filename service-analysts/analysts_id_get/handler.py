import os
import json
from bson import ObjectId
from mongoengine import connect
from utils.response import Response
from utils.serializable import serialize_document
from utils.model import User  # Importamos el modelo de MongoEngine


def handler_function(event, context):
    """
        GET handler para obtener la información de un analista, incluyendo sus assignedBusinesses.
        Se espera que event["pathParameters"]["id"] contenga el id del analista.
    """
    try:
        path_params = event.get("pathParameters", {})
        analyst_id_str = path_params.get("id")
        if not analyst_id_str:
            return Response(
                status_code=400,
                body={"error": "Falta el parámetro 'id'"}
            ).to_dict()

        # Convertir a ObjectId
        try:
            analyst_id = ObjectId(analyst_id_str)
        except Exception:
            return Response(
                status_code=400,
                body={"error": "ID del analista no es válido"}
            ).to_dict()

        # Buscar el analista con MongoEngine
        analyst = User.objects(id=analyst_id).first()
        if not analyst:
            return Response(
                status_code=404,
                body={"error": "Usuario no encontrado"}
            ).to_dict()

        analyst_serializer = serialize_document(analyst.to_mongo().to_dict())
        if "password" in analyst_serializer:
            del analyst_serializer["password"]

        return Response(
            status_code=200,
            body={"data": analyst_serializer}
        ).to_dict()
    except Exception as e:
        return Response(
            status_code=500,
            body={"error": "Error interno", "details": str(e)}
        ).to_dict()

if __name__ == "__main__":
    event = {
        "pathParameters": {
            "id": "67cbef9c0a92ce0e68e9dfb9",
        }
    }
    print(handler_function(event=event, context=None))
