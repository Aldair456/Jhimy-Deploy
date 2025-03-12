import json
import os
from mongoengine import connect
from bson import ObjectId
import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-businesses")

from utils.model import Business  # Asegúrate de importar el modelo correcto
from utils.response import Response  # Importa la clase Response
from utils.serializable import serialize_document  # Importa la función de serialización

"""""
1️ Se conecta a la base de datos MongoDB.
2️ Extrae el businessId de la URL.
3️ Busca el negocio en MongoDB.
4️ Extrae el analystId del cuerpo de la solicitud.
5️ Elimina al analista de la lista analistaIds.
6️ Serializa y devuelve el negocio actualizado.
"""
def lambda_handler(event, context):
    # Conectar a la base de datos
    connect(db=os.environ['MY_DATABASE_NAME'], host=os.environ['DATABASE_URL'])

    # Obtener el businessId desde los parámetros de la URL
    business_id = event.get("pathParameters", {}).get("businessId")
    if not business_id:
        return Response(status_code=400, body={"error": "Falta el businessId"}).to_dict()

    # Buscar el negocio en la base de datos
    business = Business.objects(id=business_id).first()
    if not business:
        return Response(status_code=404, body={"error": "Negocio no encontrado"}).to_dict()

    # Obtener el analistaId desde el cuerpo de la solicitud
    body = json.loads(event.get("body", "{}"))
    analyst_id = body.get("analystId")
    if not analyst_id:
        return Response(status_code=400, body={"error": "Falta el analystId"}).to_dict()

    # Remover el analista de la lista
    if ObjectId(analyst_id) in [a for a in business.analistaIds]:
        business.update(pull__analistaIds=ObjectId(analyst_id))
        business.reload()

    # Serializar el negocio antes de enviarlo en la respuesta
    business_serialized = serialize_document(business.to_mongo().to_dict())

    return Response(
        status_code=200,
        body={"message": "Analista removido correctamente", "business": business_serialized}
    ).to_dict()




if __name__ == "__main__":
    # Simulación de prueba local
    test_event = {
        "pathParameters": {"businessId": "67802e0a80547b162bf07dd0"},
        "body": json.dumps({"analystId": "678a9923f6a08c8217b3576b"})
    }
    print(lambda_handler(test_event, None))
