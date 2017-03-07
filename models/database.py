from pymongo import MongoClient
from config.database import DATABASE_HOST, DATABASE_NAME, COLLECTIONS


def get_mongo_cli():
    return MongoClient(DATABASE_HOST)


def get_database():
    return get_mongo_cli()[DATABASE_NAME]


def get_collection(collectionName):
    if collectionName in COLLECTIONS:
        return get_database()[collectionName]
    raise Exception("Collection does not exist")
