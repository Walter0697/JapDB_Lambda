import json
import os
from pymongo import MongoClient
from bson.json_util import dumps

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
CORS_ORIGIN = os.getenv("CORS_ORIGIN")

def list(event, context):
    url = "mongodb://" + DB_USERNAME + ":" + DB_PASSWORD + "@" + DB_HOST + ":" + DB_PORT + "/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&ssl=true"
    db_client = MongoClient(url)
    db = db_client.japdb

    bookCol = db["book"]
    allBooks = bookCol.find({})
    output = []
    for book in allBooks:
        output.append({
            "version": book["version"],
            "identifier": book["identifier"],
            "translation": book["translation"],
            "chapter": book["chapter"],
        })

    body = {
        "result": output,
    }

    response = {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': CORS_ORIGIN,
            'Access-Control-Allow-Methods': 'GET'
        },
        "body": dumps(body),
    }

    return response