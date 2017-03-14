from celery import task
from utils.stock_profile import update_stock_profile
from config.logs import logging


@task()
def run_update_for_ticker(ticker):
    logging.info("Running update for {0}".format(ticker))
    update_stock_profile(ticker)


@task()
def queue_stock_matrix_update():
    logging.info("Queueing Tickers")
    run_update_for_ticker.delay("AAPL")
    run_update_for_ticker.delay("GOOG")
