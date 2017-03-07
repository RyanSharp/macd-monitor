from models.classes import Account
from models.database import get_collection
from config.database import ACCOUNT_COLLECTION
from utils.errors import EntityAlreadyExists
import hashlib
import uuid


def find_one_account(query):
    collection = get_collection(ACCOUNT_COLLECTION)
    account = collection.find_one(query)
    if account is not None:
        return Account(account)
    return None


def get_account_by_session(session):
    return find_one_account({"session": session})


def get_account_by_username(username):
    return find_one_account({"username": username})


def create_account(username, password):
    account = get_account_by_username(username)
    if account is not None:
        raise EntityAlreadyExists("Username already in use")
    salt = uuid.uuid4().hex
    password = "{0}{1}".format(password, salt)
    password = hashlib.sha512(password).hexdigest()
    session = hashlib.sha256("{0}.{1}".format(username, uuid.uuid4().hex)).hexdigest()
    account = Account(dict(username=username,
                           salt=salt,
                           hashed_pw=password,
                           session=session))
