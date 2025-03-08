import datetime
from bson import ObjectId
from mongoengine import Document

def serialize_document(doc):
    """
    Convierte un objeto en una versión serializable a JSON.
    - Convierte ObjectId a string.
    - Convierte datetime a formato ISO 8601.
    - Convierte modelos de MongoEngine en diccionarios.
    - Soporta listas, tuplas y conjuntos.
    """
    if isinstance(doc, (list, tuple, set)):  # Manejo de colecciones
        return [serialize_document(item) for item in doc]

    if isinstance(doc, dict):  # Manejo de diccionarios
        return {key: serialize_document(value) for key, value in doc.items()}

    if isinstance(doc, ObjectId):  # Convierte ObjectId a string
        return str(doc)

    if isinstance(doc, datetime.datetime):  # Convierte datetime a formato ISO 8601
        return doc.isoformat()

    if isinstance(doc, Document):  # Convierte modelos de MongoEngine en diccionarios JSON serializables
        serialized_doc = doc.to_mongo().to_dict()
        return serialize_document(serialized_doc)

    return doc  # Retorna otros tipos sin modificaciones (int, str, float, bool)

