import json
import os
from pymongo import MongoClient
from bson.json_util import dumps

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
CORS_ORIGIN = os.getenv("CORS_ORIGIN")

def reset(event, context):
    url = "mongodb://" + DB_USERNAME + ":" + DB_PASSWORD + "@" + DB_HOST + ":" + DB_PORT + "/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&ssl=true"
    db_client = MongoClient(url)
    db = db_client.japdb

    bookCol = db["book"]
    wordCol = db["word"]
    bookWordCol = db["bookWord"]

    bookCol.drop()
    wordCol.drop()
    bookWordCol.drop()