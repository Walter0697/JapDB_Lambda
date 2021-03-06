import boto3
import json
s3_client = boto3.client('s3')
import os
from pymongo import MongoClient

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def dictionaryjson(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    json_file_name = event['Records'][0]['s3']['object']['key']
    json_object = s3_client.get_object(Bucket=bucket,Key=json_file_name)

    # starting database instance
    url = "mongodb://" + DB_USERNAME + ":" + DB_PASSWORD + "@" + DB_HOST + ":" + DB_PORT + "/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&ssl=true"
    db_client = MongoClient(url)
    db = db_client.japdb

    jsonFileReader = json_object['Body'].read()
    jsonDict = json.loads(jsonFileReader)

    language = jsonDict["language"]
    version = jsonDict["version"]
    bookInfo = jsonDict["book"]
    chapterInfo = bookInfo["chapter"]
    chapterType = bookInfo["type"]
    wordList = jsonDict["words"]
    grammar = jsonDict["grammar"]

    print("Updating " + bookInfo["identifier"] + ", Chapter " + chapterInfo["number"] + " from " + bookInfo["translation"]["local"] +  ".v" + version)

    bookCol = db["book"]
    currentBook = bookCol.find_one({ "identifier": bookInfo["identifier"] })
    if currentBook:
        # if current book exists, check the version
        if currentBook["version"] == version:
            print("Detected same version, will not update")
            return
        # update it if version is different
        bookCol.update_one({
            "identifier": bookInfo["identifier"]
        }, {
            "$set": { 
                "translation": bookInfo["translation"],
                "chapter": chapterInfo,
                "version": version,
                "language": language,
                "grammar": grammar,
                "type": chapterType,
            } 
            
        })
        print("updated book")
    else:
        # else, create it
        bookCol.insert_one({
            "identifier": bookInfo["identifier"],
            "translation": bookInfo["translation"],
            "chapter": chapterInfo,
            "version": version,
            "language": language,
            "grammar": grammar,
            "type": chapterType,
        })
        currentBook = bookCol.find_one({ "identifier": bookInfo["identifier"] })
        print("created book")

    # adding words to the database
    wordCol = db["word"]
    adding_words = []
    for word in wordList:
        print("checking " + word["identifier"])
        currentWord = wordCol.find_one({ "identifier": word["identifier"] })
        if currentWord:
            print("updating " + word["identifier"])
            meanings = currentWord["meaning"]
            new_meaning = []
            exist = False
            for meaning in meanings:
                if meaning["bookid"] == currentBook["_id"]:
                    new_meaning.append({
                        "bookid": currentBook["_id"],
                        "meaning": word["meaning"],
                        "source": word["source"],
                        "data": word["data"],
                        "word": word["word"],
                        "pronounce": word["pronounce"],
                        "language": language,
                    })
                    exist = True
                else:
                    new_meaning.append(meaning)
                  
            if not exist:
                new_meaning.append({
                    "bookid": currentBook["_id"],
                    "meaning": word["meaning"],
                    "source": word["source"],
                    "data": word["data"],
                    "word": word["word"],
                    "pronounce": word["pronounce"],
                    "language": language,
                })
              
            wordCol.update_one({
                "identifier": word["identifier"]
            }, {
                "$set": {
                    "meaning": new_meaning,
                }
            }) 
        else:
            newWord = {
                "identifier": word["identifier"],
                "meaning": [
                    {
                        "bookid": currentBook["_id"],
                        "meaning": word["meaning"],
                        "source": word["source"],
                        "pronounce": word["pronounce"],
                        "data": word["data"],
                        "language": language,
                        "word": word["word"],
                    }    
                ],
            }
            wordCol.insert_one(newWord)
            
        adding_words.append(word["identifier"])
        
    bookWordCol = db["bookWord"]
    currentBookWord = bookWordCol.find_one({ "bookId": currentBook["_id"] })
    if currentBookWord:
        bookWordCol.update_one({
            "bookId": currentBook["_id"] 
        }, {
            "$set": { 
                "wordList": adding_words
            } 
        })
        print("updated book word")
    else:
        newWord = {
            "bookId": currentBook["_id"],
            "wordList": adding_words
        }
        bookWordCol.insert_one(newWord)
        print("created book word")
