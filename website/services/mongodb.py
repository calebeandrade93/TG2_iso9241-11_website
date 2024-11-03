from pymongo import MongoClient
import os

class Mongodb:
    def __init__(self):
        self.mongo_uri = os.environ.get('MONGO_URI')
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.TelaAuditDB
        print('Instanciou o banco de dados')

    def insert_user(self, user):
        print(f'entrou na funcao insert_user com o usuario {user.get("name")}')
        self.db.userData.insert_one(user)
    
    def get_user(self, email):
        user = self.db.userData.find_one({"email": email})
        return user
    
    def get_user_by_id(self, user_id):
        user = self.db.userData.find_one({"_id": user_id})
        return user
    
    def update_user(self, email, updates):
        self.db.userData.update_one({"email": email}, {"$set": updates})
    
    def get_user_checklist(self, user_id):
        checklists = self.db.userChecklist.find({"user": user_id})
        return list(checklists)
    
    def get_checklist_by_id(self, checklist_id):
        checklist = self.db.userChecklist.find_one({"_id": checklist_id})
        return checklist

    

        