from mongoengine import DateTimeField,ObjectIdField,connect ,Document,BooleanField, StringField, FloatField, ListField, EmbeddedDocument, EmbeddedDocumentField, IntField, ReferenceField
import os
import datetime

# 📌 Modelo para Contactos

os.environ['DATABASE_URL'] = "mongodb+srv://admin:gJ66UV7FD1qs6jG0@valetest.8gw0zdt.mongodb.net/vera-app?retryWrites=true&w=majority"
os.environ['MY_DATABASE_NAME'] = "vera-app"

# Conectar a la base de datos usando la URL de conexión completa
connect(db=os.environ['MY_DATABASE_NAME'], host=os.environ['DATABASE_URL'])
class Contact(EmbeddedDocument):
    nombre = StringField(required=True)
    cargo = StringField(required=True)
    telefono = StringField()
    email = StringField()
    meta = {'collection': 'Contact'}

class Evaluator(Document):
    name = StringField(required=True)
    users = ListField(ReferenceField("User"))  # ✅ Usar cadena para evitar dependencias circulares
    businesses = ListField(ReferenceField("Business"))
    deals = ListField(ReferenceField("Deal"))

    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    meta = {'collection': 'Evaluator'}

class User(Document):
    username = StringField(unique=True, required=True)
    password = StringField(required=True)
    role = StringField(choices=["ADMIN", "ANALYST"], required=True)
    evaluatorId = ReferenceField("Evaluator", required=True, reverse_delete_rule=2)  # Ref a Evaluator
    assignedBusinessIds = ListField(ReferenceField("Business"))  # Relación con Business (en el orm lo maneja como objtos)
    name = StringField()
    image =StringField()
    email = StringField()#se quito el unico
    emailVerified = BooleanField(default=False)
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    meta = {'collection': 'User'}




class User(Document):
    username = StringField(unique=True, required=True)
    password = StringField(required=True)
    role = StringField(choices=["ADMIN", "ANALYST"], required=True)
    evaluatorId = ReferenceField("Evaluator", required=True, reverse_delete_rule=2)
    assignedBusinessIds = ListField(ReferenceField("Business"))
    name = StringField()
    image = StringField()
    email = StringField()  # Se quitó la restricción de único
    emailVerified = BooleanField(default=False)
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)
    meta = {'collection': 'User'}

# 📌 Modelo para FinancialStatement
class FinancialStatement(Document):
    businessId = ReferenceField("Business", required=True)
    type = StringField(choices=["official", "draft"])
    years = ListField(IntField())
    datapoints = ListField(ReferenceField("FinancialDatapoint"))
    currency = StringField(default="PEN")
    scaleType = StringField(default="THOUSANDS")
    status = StringField(choices=["pending", "confirmed", "cancelled", "official"])
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)
    meta = {'collection': 'FinancialStatement'}

# 📌 Modelo para Business
class Business(Document):
    name = StringField(required=True)
    ruc = StringField(required=True)
    razonSocial = StringField(required=True)
    contactos = ListField(EmbeddedDocumentField(Contact))
    ejecutivoCuenta = StringField()
    analistaIds = ListField(ReferenceField("User"))
    deals = ListField(ReferenceField("Deal"))
    evaluatorId = ReferenceField("Evaluator")
    financialStatementId = ReferenceField("FinancialStatement", required=False)
    financialStatements = ListField(ReferenceField("FinancialStatement"))
    currency = StringField(default="PEN")
    scaleType = StringField(default="THOUSANDS")
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)
    meta = {'collection': 'Business'}



# 📌 Modelo para Deal
class Deal(Document):
    title = StringField(required=True)
    status = StringField(required=True)
    business = ReferenceField(Business)
    value = FloatField()
    evaluator = ReferenceField(Evaluator)
    createdAt = IntField()
    updatedAt = IntField()
    meta = {'collection': 'Deal'}

# 📌 Modelo para DetailItem
class DetailItem(EmbeddedDocument):
    name = StringField(required=True)
    value = FloatField(required=True)
    meta = {'collection': 'DetailItem'}
# 📌 Modelo para FinancialDatapoint


# model Year {
#   id                  String               @id @default(auto()) @map("_id") @db.ObjectId
#   year                Int
#   financialDatapoints FinancialDatapoint[]
#   createdAt           DateTime             @default(now())
#   updatedAt           DateTime             @updatedAt
# }

class Year(EmbeddedDocument):
    year = IntField()
    financialDatapoints = ListField(ReferenceField("FinancialDatapoint"))
    createdAt = IntField()
    updatedAt = IntField()
    meta = {'collection': 'Year'}
    }
class FinancialDatapoint(Document):
    businessId = ReferenceField("FinancialStatement", required=True)
    value = FloatField(required=True)
    details = ListField(EmbeddedDocumentField(DetailItem))
    accountId = ReferenceField("Account")
    financialStatementId = ReferenceField("FinancialStatement")
    yearId= ReferenceField("Year",required=True)
    createdAt = IntField()
    updatedAt = IntField()
    meta = {'collection': 'FinancialDatapoint'}

# 📌 Modelo para Account
class Account(Document):
    name = StringField(unique=True, required=True)
    displayName = StringField()
    statement = StringField()
    tags = ListField(StringField())
    valueType = StringField()
    priority = IntField()
    financialDatapoints = ListField(ReferenceField(FinancialDatapoint))
    meta = {'collection': 'Account'}

