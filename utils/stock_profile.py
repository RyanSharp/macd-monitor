from models.classes import HoldingProfile
from models.database import get_collection
from utils.macd import get_quote_for_ticker, get_seed_data_for_ticker
from utils.archived_update import get_or_create_archive
from config.database import HOLDING_PROFILES_COLLECTION
from utils.errors import EntityAlreadyExists, QuoteNotFound
from utils.schedule import should_sync_run
from config.logs import logging
import datetime


def get_stock_profile(ticker):
    '''
    Returns a stock profile for a ticker if exists
    '''
    collection = get_collection(HOLDING_PROFILES_COLLECTION)
    profile = collection.find_one({"ticker": ticker})
    if profile is not None:
        return HoldingProfile(profile)
    return None


def create_stock_profile(ticker):
    '''
    Creates stock profile.  Verifies that stock data exists (from yahoo finance)
    Verifies that profile does not exist already
    Creates profile, populates data
    '''
    quote = get_quote_for_ticker(ticker)
    if quote is not None:
        profile = get_stock_profile(ticker)
        if profile is None:
            historical_data = get_seed_data_for_ticker(ticker)
            profile = HoldingProfile(dict(ticker=ticker))
            for price in historical_data:
                archived_update = get_or_create_archive(ticker, int(price[1].strftime("%Y%m%d")))
                profile.update_profile(price[0], int(price[1].strftime("%Y%m%d")), archived_update)
            profile.commit()
            return profile
        else:
            raise EntityAlreadyExists("Profile already exists for ticker")
    else:
        raise QuoteNotFound("No quote for ticker")


def update_stock_profile(ticker):
    '''
    Updates stock profile based on latest data from Yahoo finance
    '''
    if not should_sync_run():
        logging.info("Schedule does not allow update")
        return False
    quote = get_quote_for_ticker(ticker)
    profile = get_stock_profile(ticker)
    if quote is None or profile is None:
        logging.info("Missing quote or profile")
        return False
    date_int = int(datetime.datetime.now().strftime("%Y%m%d"))
    archived_update = get_or_create_archive(ticker, date_int)
    profile.update_profile(quote["price"], date_int, archived_update)
    profile.commit()
    return True


def list_stock_profiles():
    '''
    Returns a generator for surface stock profile data
    '''
    collection = get_collection(HOLDING_PROFILES_COLLECTION)
    profiles = collection.find({}, {"ticker": 1})
    for profile in profiles:
        yield HoldingProfile(profile)


def run_trivial_analysis(ticker):
    profile = get_stock_profile(ticker)
    if profile is not None:
        historical_data = profile.get_property("recent_data").get_val()[-3:]
        macd_diff_line = [(x.get_property("ema12").get_val() -
                           x.get_property("ema26").get_val() -
                           x.get_property("macd_ema9").get_val())
                          for x in historical_data]
        diff_1 = (macd_diff_line[1] - macd_diff_line[0])/macd_diff_line[0]
        diff_2 = (macd_diff_line[2] - macd_diff_line[1])/macd_diff_line[1]
        if diff_1 < 0.08 and diff_1 > -0.1 and diff_2 > 0.11:
            # Trivial analysis indicates further analysis
            return {"data": macd_diff_line, "diff_1": diff_1, "diff_2": diff_2}
    return False
