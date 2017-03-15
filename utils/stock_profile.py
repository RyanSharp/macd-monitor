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
                profile.update_profile(price[0], int(price[1].strftime("%Y%m%d")))
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
        yield profile
