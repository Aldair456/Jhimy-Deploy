import logging
import os
import json
import datetime
from pymongo import MongoClient

# Configurar el logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
import sys
sys.path.append(r"C:\Users\semin\OneDrive\Escritorio\MARCELO\jhimy\migracion\service-eeff")

from utils.model import FinancialStatement, FinancialDatapoint,DetailItem  # Asegúrate de importar los modelos correctos
from utils.response import Response  # Importa la clase Response
# Configurar conexión a MongoDB utilizando las variables de entorno
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("MY_DATABASE_NAME", "default_db")  # Usa MY_DATABASE_NAME

if not MONGO_URI:
    raise Exception("La variable de entorno MONGO_URI no está definida.")

if not DATABASE_NAME:
    raise Exception("La variable de entorno MY_DATABASE_NAME no está definida.")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]  # Se especifica la base de datos

# Función para obtener datos de MongoDB
def obtener_datos_mongodb():
    collection = db["Account"]
    return {
        doc["name"]: {
            "id": str(doc["_id"]),
            "displayName": doc["displayName"],
            "statement": doc["statement"],
            "tags": doc["tags"],
            "valueType": doc["valueType"],
            "priority": doc["priority"]
        }
        for doc in collection.find()
    }

# Obtener mapeo de cuentas
ACCOUNT_MAPPING = obtener_datos_mongodb()

def lambda_handler(event, context):
    try:
        # Se espera que el evento contenga "statement_id" y "output" con la estructura especificada
        financial_data = {
            "financialStatementId": event["statement_id"],
            "output": event["output"]
        }

        # Insertar FinancialDatapoints
        datapoints = []
        for item in financial_data["output"]:
            account_info = ACCOUNT_MAPPING.get(item["name"])
            if not account_info:
                logger.warning(f"⚠ Advertencia: No se encontró ID para '{item['name']}' en MongoDB.")
                continue

            datapoint = FinancialDatapoint(
                value=item["value"],
                details=[DetailItem(name=d["name"], value=d["value"]) for d in item["details"]],
                accountId=account_info["id"],
                financialStatementId=financial_data["financialStatementId"],
                year=int(item["year"]),
                createdAt=datetime.datetime.utcnow(),
                updatedAt=datetime.datetime.utcnow()
            )
            datapoint.save()
            datapoints.append(datapoint)

        if not datapoints:
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "No se insertaron FinancialDatapoints."})
            }

        try:
            statement_id = financial_data["financialStatementId"]
            resultado = FinancialStatement.objects(id=statement_id).update_one(
                set__status="COMPLETE",
                set__updatedAt=datetime.datetime.utcnow()
            )

            if not resultado:
                logger.warning(f"⚠️ No se encontró el FinancialStatement con ID {statement_id}.")
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": f"No se encontró el FinancialStatement con ID {statement_id}."})
                }
            logger.info(f"✅ FinancialStatement con ID {statement_id} actualizado a 'COMPLETE'.")

        except Exception as e:
            logger.error(f"❌ Error al actualizar el FinancialStatement: {e}", exc_info=True)
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Error al actualizar el estado del FinancialStatement."})
            }

        return {"statusCode": 200, "body": json.dumps({"message": "FinancialDatapoints insertados correctamente."})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": f"Error: {str(e)}"})}

if __name__ == "__main__":
    # Ejemplo de JSON recibido
    event = {
        "statement_id": "67cf667518e748a4cbb91678",
        "output": [
            {
                "name": "PERIOD_RESULTS",
                "value": 397370,
                "year": 2022,
                "details": [
                    {
                        "name": "Resultado del ejercicio",
                        "value": 397370
                    }
                ]
            },
            {
                "name": "ACCUMULATED_RESULTS",
                "value": -315618,
                "year": 2022,
                "details": [
                    {
                        "name": "Resultados acumulados",
                        "value": -315618
                    }
                ]
            },
            {
                "name": "CASH",
                "value": 67564,
                "year": 2022,
                "details": [
                    {
                        "name": "Efectivo y equivalentes de efectivo",
                        "value": 67564
                    }
                ]
            },
        ]
    }
    print(lambda_handler(event=event, context=None))
