import os
import sys

# Obtener la ruta del directorio padre
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-analysts")

#------------
import os
import json
from bson import ObjectId
from mongoengine import connect, NotUniqueError, get_db
from utils.response import Response
from utils.serializable import serialize_document
from utils.model import User, Business

def handler_function(event, context):
    """
    PATCH handler para asignar un negocio a un analista usando una transacción MongoEngine.
    """
    try:
        # Extraer el parámetro de ruta "id" del analista
        path_params = event.get("pathParameters", {})
        analyst_id_str = path_params.get("id")
        if not analyst_id_str:
            return Response(status_code=400, body={"error": "Falta el parámetro de ruta 'id'"}).to_dict()

        # Convertir a ObjectId
        try:
            analyst_id = ObjectId(analyst_id_str)
        except Exception:
            return Response(status_code=400, body={"error": "ID del analista no es válido"}).to_dict()

        # Extraer y parsear el body JSON
        body = event.get("body")
        if not body:
            return Response(status_code=400, body={"error": "Falta el cuerpo de la solicitud"}).to_dict()
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return Response(status_code=400, body={"error": "El cuerpo no es un JSON válido"}).to_dict()

        business_id_str = body.get("businessId")
        if not business_id_str:
            return Response(status_code=400, body={"error": "Falta 'businessId' en el cuerpo"}).to_dict()

        # Convertir a ObjectId
        try:
            business_id = ObjectId(business_id_str)
        except Exception:
            return Response(status_code=400, body={"error": "ID del negocio no es válido"}).to_dict()

        # Iniciar transacción
        db = get_db()
        with db.client.start_session() as session:
            with session.start_transaction():
                # Buscar el analista y el negocio
                analyst = User.objects(id=analyst_id).first()
                business = Business.objects(id=business_id).first()

                if not analyst:
                    return Response(status_code=404, body={"error": "Analista no encontrado"}).to_dict()

                if not business:
                    return Response(status_code=404, body={"error": "Negocio no encontrado"}).to_dict()


                # Agregar analyst_id a analistaIds del negocio si aún no está asignado
                if analyst_id not in business.analistaIds:
                    business.analistaIds.append(analyst_id)
                    business.save(session=session)

                # Serializar analista actualizado
                updated_analyst = serialize_document(analyst.to_mongo().to_dict())

        return Response(status_code=200, body={"data": updated_analyst}).to_dict()

    except NotUniqueError:
        return Response(status_code=409, body={"error": "Conflicto de datos. La asignación ya existe."}).to_dict()
    except Exception as e:
        return Response(status_code=500, body={"error": "Error al asignar negocio", "details": str(e)}).to_dict()


# Bloque opcional para pruebas locales
if __name__ == "__main__":
    test_event = {
        "pathParameters": {"id": "67770eace3a1abad30f4cd03"},  # Extrae el id del analista
        "body": json.dumps({"businessId": "6786e21b6106b8b2141497fd"})
    }
    response = handler_function(test_event, {})
    print("Respuesta de la función Lambda:")
    print(response)
