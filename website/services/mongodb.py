from pymongo import MongoClient
import os

class Mongodb:
    def __init__(self):
        self.mongo_uri = os.environ.get('MONGO_URI')
        print(f"Mongo URI: {self.mongo_uri}")
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.TelaAuditDB
        print('Instanciou o banco de dados')

    def insert_user(self, user):
        print(f'entrou na funcao insert_user com o usuario {user}')
        self.db.userData.insert_one(user)
        