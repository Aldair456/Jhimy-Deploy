import json
import os
from mongoengine import connect
from bson import ObjectId
from utils.model import FinancialStatement, Year, FinancialDatapoint, Account
from utils.response import Response


#falta probar
def lambda_handler(event, context):
    try:
        connect(db=os.environ['MY_DATABASE_NAME'], host=os.environ['DATABASE_URL'])

        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "No autorizado"}).to_dict()

        body = json.loads(event.get("body", "{}"))
        business_id = body.get("businessId")
        statement_type = body.get("type")
        years = body.get("years", [])
        data = body.get("data", {})

        if not business_id or not statement_type or not years:
            return Response(status_code=400, body={"error": "Faltan datos requeridos (businessId, type, o years)"}).to_dict()

        year_objects = []
        for year in years:
            year_obj, created = Year.objects.get_or_create(year=year)
            year_objects.append(year_obj)

        statement = FinancialStatement(
            businessId=business_id,
            type=statement_type,
            years=year_objects
        )
        statement.save()

        datapoints = []
        for account_id, year_values in data.items():
            account = Account.objects(id=ObjectId(account_id)).first()
            if not account:
                continue

            for year in years:
                year_obj = next((y for y in year_objects if y.year == year), None)
                if not year_obj:
                    continue

                value = year_values.get("value", 0)
                details = [
                    {"name": detail["itemName"], "value": detail["yearValues"].get(str(year), 0)}
                    for detail in year_values.get("details", [])
                ]

                datapoint = FinancialDatapoint(
                    businessId=business_id,
                    value=value,
                    details=details,
                    account=account,
                    year=year_obj,
                    financialStatement=statement
                )
                datapoints.append(datapoint)

        if datapoints:
            FinancialDatapoint.objects.insert(datapoints)

        return Response(status_code=201, body=statement.to_mongo().to_dict()).to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error interno", "details": str(e)}).to_dict()
