import json
import os
from mongoengine import connect
from bson import ObjectId
from utils.model import Business  # Asegúrate de importar el modelo correcto
from utils.response import Response  # Importa la clase Response
from utils.serializable import serialize_document  # Importa la función de serialización


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
    if ObjectId(analyst_id) in [a.id for a in business.analistaIds]:
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
        "body": json.dumps({"analystId": "67cbed1bd74313ab7499648c"})
    }
    print(lambda_handler(test_event, None))
