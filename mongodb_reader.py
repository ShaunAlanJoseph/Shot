import os
from dotenv import load_dotenv
from traceback import print_exc
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class MongoClient_RequiredParameter(Exception):
    def __init__(self, parameter: str = None):
        if parameter is None:
            self.message = f"Required parameter wasn't passed."
        else:
            self.message = f"Required parameter wasn't passed: {parameter}"
        super().__init__(self.message)


def get_mongo_client(user_name: str = None, user_password: str = None, mongo_host_name: str = None):
    load_dotenv()
    if user_name is None:
        user_name = os.environ["MONGODB_USER_NAME"]
    if not user_name:
        raise MongoClient_RequiredParameter("user_name")
    if user_password is None:
        user_password = os.environ["MONGODB_USER_PASSWORD"]
    if not user_password:
        raise MongoClient_RequiredParameter("user_password")
    if mongo_host_name is None:
        mongo_host_name = os.environ["MONGODB_HOST_NAME"]
    if not mongo_host_name:
        raise MongoClient_RequiredParameter("mongo_host_name")
    uri = f"mongodb+srv://{user_name}:{user_password}@{mongo_host_name}/?retryWrites=true&w=majority"
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command("ping")
        return client
    except Exception as e:
        print_exc()
