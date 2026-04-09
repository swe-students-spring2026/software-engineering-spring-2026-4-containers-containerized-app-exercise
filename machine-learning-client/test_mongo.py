from pymongo import MongoClient 

client = MongoClient('mongodb://admin:secret@localhost:27017/')
db = client['mydatabase']
collection = db['records']

collection.insert_one({'name': 'Alice', 'age': 30})
print("Inserted")
