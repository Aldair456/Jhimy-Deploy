import os
import json
from mongoengine import connect, DoesNotExist, NotUniqueError
from utils.response import Response
from utils.serializable import serialize_document
from utils.model import User  # Importamos el modelo de MongoEngine
from bson import ObjectId



def handler_function(event, context):
    """
    PATCH handler para actualizar un analista usando MongoEngine.
    """
    try:
        path_params = event.get("pathParameters", {})
        analyst_id = path_params.get("id")
        if not analyst_id:
            return Response(status_code=400, body={"error": "Falta el parámetro 'id'"}).to_dict()

        body = event.get("body")
        if not body:
            return Response(status_code=400, body={"error": "Falta el cuerpo de la solicitud"}).to_dict()

        if isinstance(body, str):
            body = json.loads(body)

        update_fields = {k: v for k, v in body.items() if k in ["name", "email", "username"]}
        if not update_fields:
            return Response(status_code=400, body={"error": "No hay campos para actualizar"}).to_dict()

        # Buscar y actualizar analista
        analyst = User.objects.get(id=ObjectId(analyst_id))
        analyst.update(**update_fields)
        analyst.reload()

        # Serializar el documento actualizado
        updated_analyst_serializer = serialize_document(analyst.to_mongo().to_dict())
        updated_analyst_serializer.pop("password", None)

        return Response(status_code=200, body={"data": updated_analyst_serializer}).to_dict()

    except DoesNotExist:
        return Response(status_code=404, body={"error": "Usuario no encontrado"}).to_dict()
    except NotUniqueError as e:
        return Response(status_code=400,
                        body={"error": "El nombre de usuario ya está en uso", "details": str(e)}).to_dict()
    except Exception as e:
        return Response(status_code=500, body={"error": "Error al actualizar analista", "details": str(e)}).to_dict()


if __name__ == "__main__":
    event = {
        "pathParameters": {"id": "67cbef9c0a92ce0e68e9dfb9"},
        "body": json.dumps({"name": "Juan Pablo", "email": "juanpablo@utec.edu.pe", "username": "juanp1"})
    }
    print(handler_function(event=event, context=None))