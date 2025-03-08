import json
import os
from bson import ObjectId
from utils.model import FinancialStatement  # Asegúrate de importar el modelo correcto
from utils.response import Response  # Importa la clase Response
from utils.serializable import serialize_document


def lambda_handler(event, context):
    try:
        # Verificar autorización con el Bearer Token
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "No autorizado"}).to_dict()

        # Obtener ID del negocio desde la URL
        business_id = event.get("pathParameters", {}).get("id")
        if not business_id or not ObjectId.is_valid(business_id):
            return Response(status_code=400, body={"error": "ID de negocio inválido"}).to_dict()

        # Buscar estados financieros asociados al negocio
        statements = FinancialStatement.objects(businessId=ObjectId(business_id))

        if not statements:
            return Response(status_code=404, body={"error": "No se encontraron estados financieros"}).to_dict()

        # Agrupar datos por año
        data_by_year = {}
        for statement in statements:
            year = str(statement.year)
            if year not in data_by_year:
                data_by_year[year] = {"SALES": 0, "COGS": 0, "OPEX": 0, "DEPRECIATION": 0, "AMORTIZATION": 0}

            for account in statement.accounts:
                account_name = account["name"].upper()
                account_value = account["value"]

                if "SALES" in account_name:
                    data_by_year[year]["SALES"] += account_value
                elif "COGS" in account_name:
                    data_by_year[year]["COGS"] += account_value
                elif "OM" in account_name:
                    data_by_year[year]["OPEX"] += account_value
                elif "DEPRECIATION" in account_name:
                    data_by_year[year]["DEPRECIATION"] += account_value
                elif "AMORTIZATION" in account_name:
                    data_by_year[year]["AMORTIZATION"] += account_value

        # Calcular ratios financieros
        ratios_by_year = {}
        for year, values in data_by_year.items():
            ventas = values["SALES"]
            costo_ventas = values["COGS"]
            gastos_operativos = values["OPEX"]
            depreciacion = values["DEPRECIATION"]
            amortizacion = values["AMORTIZATION"]

            EBITDA = ventas - costo_ventas - gastos_operativos + depreciacion + amortizacion
            utilidad_bruta = ventas - costo_ventas
            utilidad_operativa = utilidad_bruta - gastos_operativos
            utilidad_neta = utilidad_operativa  # Puedes agregar impuestos si lo deseas

            margen_bruto = (utilidad_bruta / ventas * 100) if ventas else None
            margen_operativo = (utilidad_operativa / ventas * 100) if ventas else None
            margen_ebitda = (EBITDA / ventas * 100) if ventas else None
            margen_neto = (utilidad_neta / ventas * 100) if ventas else None

            ratios_by_year[year] = {
                "ventasTotales": ventas,
                "utilidadNeta": utilidad_neta,
                "EBITDA": EBITDA,
                "margenBruto": margen_bruto,
                "margenOperativo": margen_operativo,
                "margenEBITDA": margen_ebitda,
                "margenNeto": margen_neto,
            }

        return Response(status_code=200, body=ratios_by_year).to_dict()

    except Exception as e:
        return Response(status_code=500, body={"error": "Error interno", "details": str(e)}).to_dict()


if __name__ == "__main__":
    test_event = {
        "headers": {"Authorization": "Bearer test_token"},
        "pathParameters": {"id": "67c1ebe6f2c06183ea1f7743"}
    }
    print(lambda_handler(test_event, None))
