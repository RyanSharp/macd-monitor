'''
    Author: Ryan Sharp
    Date: 03/17/2017

    Module for handling retrieval of Archive models from mongo
'''
from models.database import get_collection
from models.classes import ArchivedUpdate
from config.database import ARCHIVED_UPDATES_COLLECTION


def get_chronological_archive(ticker, limit=100, last_id=None, last_date=None):
    '''
        Returns ordered (from oldest to latest) stock data (and macd calculations) for
        ticker given limit and offset based on last_id or last_date
    '''
    collection = get_collection(ARCHIVED_UPDATES_COLLECTION)
    query_params = {"ticker": ticker}
    if last_id is not None:
        query_params["_id"] = {"$gt": last_id}
    elif last_date is not None:
        query_params["date"] = {"$gt": last_date}
    archive = collection.find(query_params).sort([("date", 1)]).limit(limit)
    for item in archive:
        yield ArchivedUpdate(item)
