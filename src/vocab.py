import json
import os
from pymongo import MongoClient
from bson.json_util import dumps

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
CORS_ORIGIN = os.getenv("CORS_ORIGIN")

def getchaptervocabs(event, context):
    url = "mongodb://" + DB_USERNAME + ":" + DB_PASSWORD + "@" + DB_HOST + ":" + DB_PORT + "/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&ssl=true"
    db_client = MongoClient(url)
    db = db_client.japdb

    identifier = event["queryStringParameters"]["identifier"]
    if not identifier:
        body = {
            "message": "no identifier found"
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

    bookCol = db["book"]
    wordCol = db["word"]
    bookwordCol = db["bookWord"]

    selected_book = bookCol.find_one({ "identifier": identifier })
    if selected_book:
        selected_bookWord = bookwordCol.find_one({ "bookId": selected_book["_id"] })
        if selected_bookWord:
            word_list_identifier = selected_bookWord["wordList"]
            all_words = wordCol.find({ "identifier": { "$in": word_list_identifier }})
            word_list = []
            for word in all_words:
                meaning = ""
                for m in word["meaning"]:
                    if m["bookid"] == selected_book["_id"]:
                        meaning = m["meaning"]
                        break

                word_list.append({
                    "identifier": word["identifier"],
                    "meaning": meaning,
                    "pronounce": word["pronounce"],
                    "data": word["data"],
                })
            body = {
                "result": word_list
            }
            response = {
                "statusCode": 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': CORS_ORIGIN,
                    'Access-Control-Allow-Methods': 'GET'
                },
                "body": dumps(body)
            }

            return response
        else:
            body = {
                "message": "cannot find the selected word list"
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
    else:
        body = {
            "message": "cannot find the selected book"
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