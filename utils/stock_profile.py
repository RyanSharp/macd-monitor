from models.classes import HoldingProfile
from models.database import get_collection
from utils.macd import get_quote_for_ticker, get_seed_data_for_ticker
from config.database import HOLDING_PROFILES_COLLECTION
from utils.errors import EntityAlreadyExists, QuoteNotFound
from utils.schedule import should_sync_run
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
        return
    quote = get_quote_for_ticker(ticker)
    profile = get_stock_profile(ticker)
    if quote is None or profile is None:
        return
    profile.update_profile(quote["price"], int(datetime.datetime.now().strftime("%Y%m%d")))
