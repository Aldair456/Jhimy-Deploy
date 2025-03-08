import os
import datetime
from utils.response import Response
from utils.model import Business, FinancialStatement
def handler(event, context):
    """
    Lambda function para obtener o crear un estado financiero asociado a un negocio.
    Se espera:
    - event["pathParameters"]["businessId"]: ID del negocio a consultar.
    """
    try:
        path_params = event.get("pathParameters", {})
        business_id = path_params.get("businessId")

        if not business_id:
            return Response(
                status_code=400,
                body={"error": "Falta el parámetro 'businessId'"}
            ).to_dict()

        # Buscar negocio
        business = Business.objects(id=business_id).first()
        if not business:
            return Response(
                status_code=500,
                body={"error": "Internal Server Error"}
            ).to_dict()

        # Si no tiene estado financiero, crearlo
        if not business.financialStatementId:
            created_financial_statement = FinancialStatement(
                years=[],
                createdAt=datetime.datetime.utcnow(),
                updatedAt=datetime.datetime.utcnow(),
                businessId=business
            ).save()

            # Asignar el estado financiero al negocio
            business.financialStatementId = created_financial_statement
            business.save()

            return Response(
                status_code=200,
                body={
                    "id": str(created_financial_statement.id),
                    "message": "Financial statement created",
                    "created": True
                }
            ).to_dict()

        return Response(
            status_code=200,
            body={
                "id": str(business.financialStatementId.id),
                "message": "Financial statement already exists",
                "created": False
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
            "businessId": "67c76aa2c0f88e26ec2fba16"
        }
    }
    print(handler(event=event, context={}))
