#
import os
import sys

sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-analysts")

#-------
import os
import json
from bson import ObjectId
from mongoengine import connect
from utils.response import Response
from utils.serializable import serialize_document
from utils.model import User, Business  # Asegúrate de importar ambos modelos

def handler_function(event, context):
    try:
        # Extraer el parámetro de ruta "id" (analyst_id)
        path_params = event.get("pathParameters", {})
        analyst_id_str = path_params.get("id")
        if not analyst_id_str:
            return Response(status_code=400, body={"error": "Falta el parámetro de ruta 'id'"}).to_dict()

        try:
            analyst_id = ObjectId(analyst_id_str)
        except Exception as e:
            return Response(status_code=400,
                            body={"error": "ID del analista no es válido", "details": str(e)}).to_dict()

        # Extraer y parsear el cuerpo de la solicitud (JSON)
        body = event.get("body")
        if not body:
            return Response(status_code=400, body={"error": "Falta el cuerpo de la solicitud"}).to_dict()

        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError as e:
                return Response(status_code=400,
                                body={"error": "El cuerpo no es un JSON válido", "details": str(e)}).to_dict()

        business_id_str = body.get("businessId")
        if not business_id_str:
            return Response(status_code=400, body={"error": "Falta 'businessId' en el cuerpo"}).to_dict()

        try:
            business_id = ObjectId(business_id_str)
        except Exception as e:
            return Response(status_code=400, body={"error": "ID del negocio no es válido", "details": str(e)}).to_dict()

        # Buscar el analista en la base de datos
        analyst = User.objects(id=analyst_id).first()
        if not analyst:
            return Response(status_code=404, body={"error": "Analista no encontrado"}).to_dict()

        # Buscar el negocio en la base de datos
        business = Business.objects(id=business_id).first()
        if not business:
            return Response(status_code=404, body={"error": "Negocio no encontrado"}).to_dict()

        # Eliminar el businessId de assignedBusinessIds del analista
        if business in analyst.assignedBusinessIds:
            analyst.assignedBusinessIds.remove(business)
            analyst.save()

        # Eliminar el analystId de analistaIds del negocio
        if analyst in business.analistaIds:
            business.analistaIds.remove(analyst)
            business.save()

        # Serializar y devolver el analista actualizado
        updated_analyst = serialize_document(analyst.to_mongo().to_dict())
        if "password" in updated_analyst:
            del updated_analyst["password"]

        return Response(status_code=200, body={"data": updated_analyst}).to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error al desasignar negocio", "details": str(e)}).to_dict()


# Bloque opcional para pruebas locales
if __name__ == "__main__":
    test_event = {
        "pathParameters": {"id": "67cbed1bd74313ab7499648c"},
        "body": json.dumps({"businessId": "6786e21b6106b8b2141497fd"})
    }
    response = handler_function(test_event, {})
    print("Respuesta de la función Lambda:")
    print(response)
# checking 