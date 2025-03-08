import os
from mongoengine import connect, disconnect
from utils.response import Response
from utils.model import User, Business  # Importamos los modelos de MongoEngine
from bson import ObjectId

# Configurar conexión a MongoDB con MongoEngine
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb+srv://admin:gJ66UV7FD1qs6jG0@valetest.8gw0zdt.mongodb.net/vera-app")

# Desconectar cualquier conexión existente antes de conectar
disconnect(alias='default')
connect(host=DATABASE_URL, alias='default')


def handler_function(event, context):
    """
    DELETE handler para eliminar un analista de la colección "User" y,
    de forma transaccional, eliminar su id de la lista de usuarios en la colección "Business".
    Se espera que event["pathParameters"]["id"] contenga el id del analista.
    La eliminación se realiza solo si el rol del usuario es 'ANALYST'.
    """
    try:
        path_params = event.get("pathParameters", {})
        analyst_id_str = path_params.get("id")

        if not analyst_id_str:
            return Response(
                status_code=400,
                body={"error": "Falta el parámetro 'id'"}
            ).to_dict()

        # Convertir ID a ObjectId
        try:
            analyst_id = ObjectId(analyst_id_str)
        except Exception:
            return Response(
                status_code=400,
                body={"error": "ID del analista no es válido"}
            ).to_dict()

        # Iniciar la transacción
        with User._get_collection().database.client.start_session() as session:
            with session.start_transaction():
                # Buscar y eliminar el usuario solo si es un ANALYST
                analyst = User.objects(id=ObjectId(analyst_id), role="ANALYST").first()
                if not analyst:
                    return Response(
                        status_code=404,
                        body={"error": "Usuario no encontrado o no es un ANALYST"}
                    ).to_dict()

                # Eliminar el usuario
                analyst.delete()

                # Remover el ID del analista de todos los negocios donde esté asignado
                Business.objects(analistaIds=ObjectId(analyst_id)).update(pull__analistaIds=ObjectId(analyst_id))

        return Response(
            status_code=204,
            body={"success": True}
        ).to_dict()

    except Exception as e:
        return Response(
            status_code=500,
            body={"error": "Error al eliminar analista", "details": str(e)}
        ).to_dict()


# Pruebas locales
if __name__ == "__main__":
    event = {
        "pathParameters": {
            "id": "67802e0a80547b162bf07dd0",
        }
    }
    print(handler_function(event=event, context={}))
