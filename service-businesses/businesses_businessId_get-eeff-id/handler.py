import os
import sys
import datetime
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-businesses")

from utils.response import Response
from utils.model import Business, FinancialStatement
from utils.serializable import serialize_document

def handler(event, context):
    """
    Lambda function para obtener o crear un estado financiero asociado a un negocio.
    Se espera:
      - event["pathParameters"]["businessId"]: ID del negocio a consultar.
    
    Flujo:
      1. Se extrae el businessId de los parámetros de ruta.
      2. Se busca el negocio en la base de datos.
      3. Se verifica que el campo financialStatements sea una lista (según el modelo).
      4. Si la lista está vacía, se crea un nuevo FinancialStatement y se añade a la lista.
      5. Si ya existe, se retorna el primer estado financiero existente.
    """
    try:
        path_params = event.get("pathParameters", {})
        business_id = path_params.get("businessId")
        if not business_id:
            return Response(
                status_code=400,
                body={"error": "Falta el parámetro 'businessId'"}
            ).to_dict()

        # Buscar el negocio
        business = Business.objects(id=business_id).first()
        if not business:
            return Response(
                status_code=500,
                body={"error": "Internal Server Error"}
            ).to_dict()

        print("paso: se encontró el negocio")

        # Asegurarse de que financialStatements sea una lista.
        if not isinstance(business.financialStatements, list):
            business.financialStatements = []
            business.save()

        # Si no tiene estado financiero, crearlo.
        if len(business.financialStatements) == 0:
            created_financial_statement = FinancialStatement(
                years=[],
                createdAt=datetime.datetime.utcnow(),
                updatedAt=datetime.datetime.utcnow(),
                businessId=business.id  # Usamos el ID del negocio
            ).save()

            # Agregar el estado financiero a la lista y guardar el negocio.
            business.financialStatements.append(created_financial_statement)
            business.save()
            print("ingresa: se creó el estado financiero")

            return Response(
                status_code=200,
                body={
                    "id": str(created_financial_statement.id),
                    "message": "Financial statement created",
                    "created": True
                }
            ).to_dict()

        # Si ya existe al menos un estado financiero, se retorna el primero.
        existing_statement = business.financialStatements[0]
        existing_statement_serialiser = serialize_document(existing_statement.to_mongo().to_dict())
        return Response(
            status_code=200,
            body={
                "id": str(existing_statement.id),
                "message": "Financial statement already exists",
                "created": False,
                "financialStatement": existing_statement_serialiser
            }
        ).to_dict()

    except Exception as e:
        return Response(
            status_code=500,
            body={"error": "Error al obtener o crear el estado financiero", "details": str(e)}
        ).to_dict()

if __name__ == "__main__":
    event = {
        "pathParameters": {
            "businessId": "67802e0a80547b162bf07dd0"
        }
    }
    print(handler(event=event, context={}))
