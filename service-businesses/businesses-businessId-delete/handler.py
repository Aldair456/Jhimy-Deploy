import os
from mongoengine import connect
import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-businesses")
from utils.response import Response
from utils.model import Business, FinancialStatement, FinancialDatapoint
""""
Conecta a MongoDB usando las variables de entorno DATABASE_URL y MY_DATABASE_NAME.
Busca el negocio (Business) por su businessId.
Elimina sus estados financieros (FinancialStatement) y los datos financieros (FinancialDatapoint) relacionados.
Finalmente, elimina el negocio (Business) de la base de datos.
"""
# Conectar a la BD
connect(
    db=os.environ.get("MY_DATABASE_NAME", "vera-app"),
    host=os.environ.get("DATABASE_URL"),
    alias="default"
)

#falta probar
def handler(event, context):
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
                status_code=404,
                body={"error": "Negocio no encontrado"}
            ).to_dict()

        # Obtener los estados financieros asociados al negocio
        fs_ids = FinancialStatement.objects(businessId=business.id).values_list('id')

        # Eliminar los FinancialDatapoint asociados a esos estados financieros
        FinancialDatapoint.objects(financialStatementId__in=fs_ids).delete()

        # Eliminar los estados financieros
        FinancialStatement.objects(businessId=business.id).delete()

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
            "businessId": "67802e0a80547b162bf07dd0"
        }
    }
    print(handler(event=event, context={}))
