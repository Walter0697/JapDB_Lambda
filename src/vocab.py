import json
import os
from pymongo import MongoClient

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def getchaptervocabs(event, context):
    url = "mongodb://" + DB_USERNAME + ":" + DB_PASSWORD + "@" + DB_HOST + ":" + DB_PORT + "/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&ssl=true"
    db_client = MongoClient(url)
    db = db_client.japdb

    identifier = event["queryStringParameters"]["identifier"]
    if not identifier:
        response = {
            "statusCode": 400,
            "message": "no identifier found",
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
            print(all_words)
            word_list = []
            for word in all_words:
                word_list.append({
                    "identifier": word["identifier"],
                    "meaning": word["meaning"],
                    "pronounce": word["pronounce"],
                    "data": word["data"],
                })
            response = {
                "statusCode": 200,
                "result": json.dumps(word_list),
            }

            return response
        else:
            response = {
                "statusCode": 404,
                "message": "cannot find the selected book"
            }

            return response
    else:
        response = {
            "statusCode": 404,
            "message": "cannot find the selected book"
        }

        return response