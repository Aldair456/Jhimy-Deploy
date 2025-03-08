import os
from mongoengine import connect
from utils.response import Response
from utils.model import Business, FinancialStatement, FinancialDatapoint

# Conectar a la BD
connect(
    db=os.environ.get("MY_DATABASE_NAME", "vera-app"),
    host=os.environ.get("DATABASE_URL"),
    alias="default"
)

#falta probar

def handler(event, context):
    """
    Lambda function para eliminar un negocio y sus datos financieros relacionados.
    Se espera:
    - event["pathParameters"]["businessId"]: ID del negocio a eliminar.
    """
    try:
        path_params = event.get("pathParameters", {})
        business_id = path_params.get("businessId")

        if not business_id:
            return Response(
                status_code=400,
                body={"error": "Falta el parámetro 'businessId'"}
            ).to_dict()

        # Buscar y eliminar el negocio
        business = Business.objects(id=business_id).first()
        if not business:
            return Response(
                status_code=404,
                body={"error": "Negocio no encontrado"}
            ).to_dict()

        # Eliminar registros financieros relacionados
        FinancialStatement.objects(businessId=business).delete()
        FinancialDatapoint.objects(businessId=business).delete()

        # Eliminar el negocio
        business.delete()

        return Response(
            status_code=200,
            body={"message": "Empresa eliminada correctamente"}
        ).to_dict()

    except Exception as e:
        return Response(
            status_code=500,
            body={"error": "No se pudo eliminar la empresa", "details": str(e)}
        ).to_dict()

if __name__ == "__main__":
    event = {
        "pathParameters": {
            "businessId": "12345"
        }
    }
    print(handler(event=event, context={}))
