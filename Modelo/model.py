from mongoengine import DateTimeField,ObjectIdField,connect ,Document,BooleanField, StringField, FloatField, ListField, EmbeddedDocument, EmbeddedDocumentField, IntField, ReferenceField
import os
import datetime

# 📌 Modelo para Contactos

os.environ['DATABASE_URL'] = "mongodb+srv://admin:gJ66UV7FD1qs6jG0@valetest.8gw0zdt.mongodb.net/vera-app?retryWrites=true&w=majority"
os.environ['MY_DATABASE_NAME'] = "vera-app"

# Conectar a la base de datos usando la URL de conexión completa
connect(db=os.environ['MY_DATABASE_NAME'], host=os.environ['DATABASE_URL'])

############   Contact   ############
# type Contact {
#   nombre      String
#   cargo      String
#   telefono   String
#   email      String
# }

class Contact(EmbeddedDocument):
    nombre = StringField()
    cargo = StringField()
    telefono = StringField()
    email = StringField()


############   User   ############
# model User {
#   id                  String     @id @default(auto()) @map("_id") @db.ObjectId
#   username            String     @unique
#   password            String
#   role                UserRole
#   evaluatorId         String     @db.ObjectId
#   evaluator           Evaluator  @relation(fields: [evaluatorId], references: [id])
#   assignedBusinessIds String[]   @db.ObjectId @default([])
#   assignedBusinesses  Business[] @relation("AnalistaBusiness", fields: [assignedBusinessIds], references: [id])
#   name                String?
#   email               String?    @unique
#   createdAt           DateTime   @default(now())
#   updatedAt           DateTime   @updatedAt
# }
class User(Document):
    username = StringField(unique=True, required=True)
    password = StringField(required=True)
    role = StringField(choices=["ADMIN", "ANALYST"], required=True)
    evaluatorId = ObjectIdField(required=True)
    evaluator = ReferenceField("Evaluator")
    name = StringField()
    email = StringField()
    emailVerified = BooleanField(default=False)
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)
    meta = {'collection': 'User'}


############   Evaluator   ############
# model Evaluator {
#   id         String     @id @default(auto()) @map("_id") @db.ObjectId
#   name       String
#   users      User[]
#   businesses Business[]
#   deals      Deal[]
#   createdAt  DateTime   @default(now())
#   updatedAt  DateTime   @updatedAt
# }

class Evaluator(Document):
    name = StringField(required=True)
    users = ListField(ReferenceField("User"))  # ✅ Usar cadena para evitar dependencias circulares
    businesses = ListField(ReferenceField("Business"))
    deals = ListField(ReferenceField("Deal"))

    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    meta = {'collection': 'Evaluator'}


############   Business   ############
# // scaleType del business es puramente visual
# // el scaleType que manda para los datapoints es el scale type del FS
# model Business {
#   id                  String               @id @default(auto()) @map("_id") @db.ObjectId
#   name                String
#   ruc                 String               @unique
#   razonSocial         String
#   contactos           Contact[]
#   ejecutivoCuenta     String
#   analistaIds         String[]             @db.ObjectId
#   analistas           User[]               @relation("AnalistaBusiness", fields: [analistaIds], references: [id])
#   deals               Deal[]
#   evaluatorId         String               @db.ObjectId
#   evaluator           Evaluator            @relation(fields: [evaluatorId], references: [id])
#   financialStatements FinancialStatement[]
#   createdAt           DateTime             @default(now())
#   updatedAt           DateTime             @updatedAt
#
#   currency    String               @default("PEN") // 'PEN', 'USD', 'EUR'
#   scaleType   String               @default("THOUSANDS") // 'millones', 'miles', 'millones'
# }
class Business(Document):
    name = StringField(required=True)
    ruc = StringField(required=True, unique=True)
    razonSocial = StringField(required=True)
    contactos = ListField(EmbeddedDocumentField(Contact))
    ejecutivoCuenta = StringField()
    analistaIds = ListField(ObjectIdField())
    analistas = ListField(ReferenceField("User"))
    deals = ListField(ReferenceField("Deal"))
    evaluatorId = ObjectIdField()
    evaluator = ReferenceField("Evaluator")
    financialStatements = ListField(ReferenceField("FinancialStatement"))
    currency = StringField(default="PEN")
    scaleType = StringField(default="THOUSANDS")
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)
    meta = {'collection': 'Business'}


############   Deal   ############
# model Deal {
#   id         String   @id @default(auto()) @map("_id") @db.ObjectId
#   title      String
#   status     String
#   businessId String   @db.ObjectId
#   business   Business @relation(fields: [businessId], references: [id])
#    value     Float
#    evaluatorId String @db.ObjectId
#    evaluator Evaluator @relation(fields: [evaluatorId], references: [id])
#   // period    String?
#   // periodId  String?  @db.ObjectId
#   createdAt  DateTime @default(now())
#   updatedAt  DateTime @updatedAt
# }

class Deal(Document):
    title = StringField(required=True)
    status = StringField(required=True)
    businessId = ObjectIdField()
    business = ReferenceField("Business")
    value = FloatField()
    evaluatorId = ObjectIdField()
    evaluator = ReferenceField("Evaluator")
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)
    meta = {'collection': 'Deal'}


############   DetailItem   ############
# type DetailItem {
#   name  String
#   value Float
# }
class DetailItem(EmbeddedDocument):
    name = StringField()
    value = FloatField()



############   FinancialDatapoint   ############

# model FinancialDatapoint {
#   id                  String       @id @default(auto()) @map("_id") @db.ObjectId
#   value               Float
#   details             DetailItem[]
#   accountId           String       @db.ObjectId
#   account             Account      @relation(fields: [accountId], references: [id])
#   financialStatementId String      @db.ObjectId
#   financialStatement  FinancialStatement @relation(fields: [financialStatementId], references: [id])
#   year                Int
#   createdAt           DateTime     @default(now())
#   updatedAt           DateTime     @updatedAt
# }

class FinancialDatapoint(Document):
    value = FloatField(required=True)
    details = ListField(EmbeddedDocumentField(DetailItem))
    accountId = ObjectIdField(required=True)
    account = ReferenceField('Account')
    financialStatementId = ObjectIdField(required=True)
    financialStatement = ReferenceField('FinancialStatement')
    year = IntField()
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)
    meta = {'collection': 'FinancialDatapoint'}


############   Account   ############

# model Account {
#   id                  String               @id @default(auto()) @map("_id") @db.ObjectId
#   name                String               @unique
#   displayName         String
#   statement           String
#   tags                String[]
#   valueType           String
#   priority            Int
#   financialDatapoints FinancialDatapoint[]
# }
class Account(Document):
    name = StringField(required=True, unique=True)
    displayName = StringField()
    statement = StringField()
    tags = ListField(StringField())
    valueType = StringField()
    priority = IntField()
    financialDatapoints = ListField(ReferenceField('FinancialDatapoint'))

    meta = {'collection': 'Account'}





############   FinancialStatement   ############

# model FinancialStatement {
#   id          String               @id @default(auto()) @map("_id") @db.ObjectId
#   businessId  String               @db.ObjectId @unique
#   business    Business             @relation(fields: [businessId], references: [id])
#   type        String               // 'official', 'draft'
#   years       Int[]
#   datapoints  FinancialDatapoint[]
#   createdAt   DateTime             @default(now())
#   updatedAt   DateTime             @updatedAt
#
#   currency    String               @default("PEN") // 'PEN', 'USD', 'EUR'
#   scaleType   String               @default("THOUSANDS") // 'units', 'millones', 'miles', 'millones'
#
#   status      String              // 'official':['official'], 'draft':['pending','confirmed','cancelled']
# }
class FinancialStatement(Document):
    businessId = ObjectIdField(required=True)
    business = ReferenceField("Business")
    type = StringField(choices=["OFFICIAL", "DRAFT"])  # 'situacional', 'auditados', 'parciales'
    years = ListField(IntField())
    datapoints = ListField(ReferenceField('FinancialDatapoint'))
    currency = StringField(default="PEN")  # 'PEN', 'USD', 'EUR'
    scaleType = StringField(default="THOUSANDS")  # 'millones', 'miles', 'millones'
    status = StringField(choices=["PENDING", "CONFIRMED", "CANCELLED", "OFFICIAL", "COMPLETE"])
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)
    meta = {'collection': 'FinancialStatement'}
