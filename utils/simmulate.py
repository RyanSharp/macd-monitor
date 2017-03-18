'''
    Author: Ryan Sharp
    Date: 03/17/2017

    Module for simmulating performance of MACD models on dictating aquisitions
'''
from utils.classify import stock_health_linear_regression
from utils.archive import get_chronological_archive
from utils.stock_profile import create_stock_profile
from models.database import get_collection
from config.database import HOLDING_PROFILES_COLLECTION, ARCHIVED_UPDATES_COLLECTION


def run_historical_analysis(ticker):
    '''
        Builds a buy/sell history for a symbol based on momentum tracking strategy
    '''
    last_date = None
    prev_ema_diff = None
    current_action = []
    actions = []
    index = -2
    while True:
        count = 0
        for item in get_chronological_archive(ticker, last_date=last_date):
            count += 1
            health_factor = item.get_property("health_factor").get_val()
            last_date = item.get_property("date").get_val()
            ema12 = item.get_property("ema12").get_val()
            ema26 = item.get_property("ema26").get_val()
            macd_ema9 = item.get_property("macd_ema9").get_val()
            if health_factor is None:
                continue
            lin_regr = stock_health_linear_regression(health_factor)
            curr_ema_diff = ema12 - ema26 - macd_ema9
            if prev_ema_diff is not None:
                ema_record = [prev_ema_diff, curr_ema_diff]
                if check_positive_momentum(lin_regr, health_factor, ema_record):
                    if current_action:
                        continue
                    index = count if count < 100 else -1
                    price = item.get_property("price").get_val()
                    current_action = ["buy", last_date, price, None]
                    actions.append(current_action)
                elif len(current_action) > 0 and count > (index + 1):
                    index = -2
                    price = item.get_property("price").get_val()
                    actions.append(["sell", last_date, price, price / current_action[2]])
                    current_action = []
            prev_ema_diff = curr_ema_diff
        if count == 0:
            break
        count = 0
    return actions


def check_positive_momentum(linear_regression_output, health_factor, ema_record):
    '''
        Checks if linear regression indicates growth increasing
    '''
    vals = [health_factor[str(x + 1) + "d"] for x in xrange(len(health_factor.keys()))]
    # return linear_regression_output[0] > linear_regression_output[-1] and\
    #     vals[0] > max(vals[1:]) and ema_record[1] > 0 and ema_record[1]/ema_record[0] > 2
    return ema_record[1] > 0 and ema_record[1]/ema_record[0] > 2


def reload_data():
    with open("config/recommended_profiles.json") as profiles:
        import json
        profiles = json.loads(profiles.read())
        archive_collection = get_collection(ARCHIVED_UPDATES_COLLECTION)
        profiles_collection = get_collection(HOLDING_PROFILES_COLLECTION)
        for ticker in profiles["tickers"]:
            profiles_collection.delete_one({"ticker": ticker})
            archive_collection.delete_many({"ticker": ticker})
            create_stock_profile(ticker)
