import json
import os
from pymongo import MongoClient
from bson.json_util import dumps

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
CORS_ORIGIN = os.getenv("CORS_ORIGIN")

def get(event, context):
    url = "mongodb://" + DB_USERNAME + ":" + DB_PASSWORD + "@" + DB_HOST + ":" + DB_PORT + "/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&ssl=true"
    db_client = MongoClient(url)
    db = db_client.japdb
    identifier = event["queryStringParameters"]["identifier"]
    if not identifier:
        body = {
            "message": "no identifier"
        }
        response = {
            "statusCode": 400,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': CORS_ORIGIN,
                'Access-Control-Allow-Methods': 'GET'
            },
            "body": json.dumps(body)
        }

        return response

    wordCol = db["word"]
    bookCol = db["book"]

    selected_word = wordCol.find_one({ "identifier": identifier })
    if not selected_word:
        body = {
            "message": "cannot find word"
        }
        response = {
            "statusCode": 404,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': CORS_ORIGIN,
                'Access-Control-Allow-Methods': 'GET'
            },
            "body": json.dumps(body)
        }

        return response

    book_id_list = []
    for meaning in selected_word["meaning"]:
        book_id_list.append(meaning["bookid"])
    
    book_list = bookCol.find({ "_id": {"$in": book_id_list }})

    output = {
        "word": selected_word,
        "books": book_list
    }

    response = {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': CORS_ORIGIN,
            'Access-Control-Allow-Methods': 'GET'
        },
        "body": dumps(output),
    }

    return response
