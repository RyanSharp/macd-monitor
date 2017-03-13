from celery import task
from models.database import get_collection
from utils.stock_profile import update_stock_profile
from config.logs import logging
from config.database import HOLDING_PROFILES_COLLECTION


@task()
def run_update_for_ticker(ticker):
    '''
    Pulls current prices for a stock and updates stored values
    '''
    logging.info("Running update for {0}".format(ticker))
    if update_stock_profile(ticker):
        logging.info("Update completed successfully")
    else:
        logging.info("Update did not complete")


@task()
def queue_stock_matrix_update():
    '''
    Queues updates for every ticker
    '''
    logging.info("Queueing Stock Updates")
    collection = get_collection(HOLDING_PROFILES_COLLECTION)
    for profile in collection.find({}, {"ticker", 1}):
        logging.info("Scheduling update for {0}".format(profile["ticker"]))
        run_update_for_ticker.delay(profile["ticker"])
