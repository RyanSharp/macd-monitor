from celery import task
from models.database import get_collection
from utils.stock_profile import update_stock_profile, run_trivial_analysis
from config.logs import logging
from config.database import HOLDING_PROFILES_COLLECTION
from utils.slack_connector import send_message
from utils.schedule import should_analysis_run
import json


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
    for profile in collection.find({}, {"ticker": 1}):
        logging.info("Scheduling update for {0}".format(profile["ticker"]))
        run_update_for_ticker.delay(profile["ticker"])


@task()
def run_eod_analysis(ticker):
    '''
    Analyze stock momentum for indicators of potential buys
    '''
    logging.info("Running EOD analysis for {0}".format(ticker))
    result = run_trivial_analysis(ticker)
    if result:
        message = "Trigger for {0}.\n{1}".format(ticker, json.dumps(result))
        send_message(message)


@task()
def queue_matrix_eod_analysis():
    '''
    Queues EOD analysis for each ticker
    '''
    logging.info("Queueing EOD Analysis")
    collection = get_collection(HOLDING_PROFILES_COLLECTION)
    if not should_analysis_run():
        return
    for profile in collection.find({}, {"ticker": 1}):
        logging.info("Scheduling update for {0}".format(profile["ticker"]))
        run_eod_analysis.delay(profile["ticker"])
