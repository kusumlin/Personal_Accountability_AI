import sys
from pymongo import MongoClient

from src.exception import CustomException
from src.logger import logging


def get_mongo_client(uri: str) -> MongoClient:
    try:
        client = MongoClient(uri)
        logging.info("MongoDB connection established")
        return client
    except Exception as e:
        raise CustomException(e, sys)
