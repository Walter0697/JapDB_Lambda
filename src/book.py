import json
import os
from pymongo import MongoClient

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def list(event, context):
    url = "mongodb://" + DB_USERNAME + ":" + DB_PASSWORD + "@" + DB_HOST + ":" + DB_PORT + "/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&ssl=true"
    client = MongoClient(url)

    db=client.japdb

    bookCol = db["book"]
    allBooks = bookCol.find({})
    
    output = []
    for book in allBooks:
        output.append({
            "identifier": book["identifier"],
            "tranlation": book["translation"],
            "chapter": book["chapter"],
        })

    body = {
        "result": json.dumps(output),
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body),
    }

    return response