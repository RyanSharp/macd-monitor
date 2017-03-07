from celery import task
from utils.stock_profile import update_stock_profile


@task()
def run_update_for_ticker(ticker):
    update_stock_profile(ticker)


@task()
def queue_stock_matrix_update():
    run_update_for_ticker.delay("AAPL")
    run_update_for_ticker.delay("GOOG")
