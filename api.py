from webapp2 import RequestHandler, WSGIApplication
from google.appengine.ext.key_range import ndb
from google.appengine.api import taskqueue
from entities import StockProfile, ExponentialMovingAverageValue, StockQuote
from macd import get_quote_for_ticker, get_seed_data_for_ticker, calibrate_macd, calculate_ema
from pytz import timezone
import httplib2
import datetime
import logging

UTC_TZ = timezone("UTC")
EASTERN = timezone("US/Eastern")

_SKIP_DATES = [
    "2017-01-02",
    "2017-01-16",
    "2017-02-20",
    "2017-04-14",
    "2017-05-29",
]


def should_sync_run():
    '''
    Prevents application from syncing if markets are closed or before/after hours
    '''
    now = UTC_TZ.localize(datetime.datetime.now())
    now = now.astimezone(EASTERN)
    if now.weekday() in [5, 6]:
        return False
    if now.hour < 5 or now.hour > 18:
        return False
    date_format = "%Y-%m-%d"
    if now.strftime(date_format) in _SKIP_DATES:
        return False
    return True


class StartTrackingTicker(RequestHandler):
    '''
    Attempts to get quote data for a ticker, if successful will generate profile
    and pull historical data
    '''
    def get(self, ticker):
        quote = get_quote_for_ticker(ticker)
        if quote is not None:
            profile = StockProfile(id=ticker,
                                   ticker=ticker)
            profile.put()
        else:
            self.response.write("No quote for ticker")


class ImportHistorical(RequestHandler):
    '''
    Grabs historical data for a stock from Jan. 1, 2016
    Generates EMAs for 26 and 12 days and MACD EMA for 9 days
    '''
    def get(self, ticker):
        profile = StockProfile.get_by_id(ticker)
        historical = get_seed_data_for_ticker(ticker)
        try:
            ema26, ema12, data = calibrate_macd(historical)
            macd_ema9 = None
            count = 0
            ema26_l = []
            ema12_l = []
            macd_ema9_l = []
            points = []
            for price in data:
                count += 1
                ema26 = calculate_ema(price, ema26, 26)
                ema12 = calculate_ema(price, ema12, 12)
                if macd_ema9 is None:
                    macd_ema9 = ema26 - ema12
                else:
                    macd_ema9 = calculate_ema(ema26 - ema12, macd_ema9, 9)
                if len(data) - count <= 100:
                    ema26_l.append(ExponentialMovingAverageValue(value=ema26))
                    ema12_l.append(ExponentialMovingAverageValue(value=ema12))
                    macd_ema9_l.append(ExponentialMovingAverageValue(value=macd_ema9))
                    points.append(StockQuote(price=price[0],
                                             date=datetime.datetime.strptime()))
            profile.points = points
            profile.ema26 = ema26_l
            profile.ema12 = ema12_l
            profile.macd_ema9 = macd_ema9_l
            profile.put()
        except Exception as e:
            logging.exception(e)


class RunPriceSyncTask(RequestHandler):
    '''
    Queues all tickers to be synced for latest data
    '''
    def get(self):
        if not should_sync_run():
            return
        profiles = StockProfile.query()
        for profile in profiles:
            taskqueue.add(url="/api/stock_tracker/update/{0}".format(profile.ticker),
                          queue_name="latest_data")


class GetLatestForTicker(RequestHandler):
    '''
    Updates profile's price, EMA, MACD values for a ticker
    '''
    def get(self, ticker):
        profile = StockProfile.get_by_id(ticker)
        quote = get_quote_for_ticker(ticker)
        price = quote["financialData"]["currentPrice"]["raw"]
        points = profile.points
        ema26_l = profile.ema26
        ema12_l = profile.ema12
        macd_ema9_l = profile.macd_ema9
        now = UTC_TZ.localize(datetime.datetime.now())
        now = now.astimezone(EASTERN)
        simple_date = datetime.datetime.strptime(now.strftime("%Y-%m-%d"), "%Y-%m-%d")
        latest_point = points[-1]
        if latest_point.date == simple_date:
            points[-1].price = price
            ema26_l[-1].value = calculate_ema(price, ema26_l[-2], 26)
            ema12_l[-1].value = calculate_ema(price, ema12_l[-2], 26)
            macd_ema9_l[-1].value =\
                calculate_ema(ema26_l[-1].value - ema12_l[-1].value,
                              macd_ema9_l[-2].value, 9)
        else:
            points.append(StockQuote(price=price,
                                     date=simple_date))
            ema26_l.append(calculate_ema(price, ema26_l[-1], 26))
            ema12_l.append(calculate_ema(price, ema12_l[-1], 26))
            macd_ema9_l.append(
                calculate_ema(ema26_l[-1].value - ema12_l[-1].value,
                              macd_ema9_l[-1].value, 9))
            points = points[1:]
            ema26_l = ema26_l[1:]
            ema12_l = ema12_l[1:]
            macd_ema9_l = macd_ema9_l[1:]
        profile.ema26 = ema26_l
        profile.ema12 = ema12_l
        profile.macd_ema9 = macd_ema9_l
        profile.points = points
        profile.put()


app = ndb.toplevel(WSGIApplication([
    ("/api/stock_tracker/new/([^/]*)", StartTrackingTicker),
    ("/api/stock_tracker/sync/([^/]*)", ImportHistorical),
    ("/api/stock_tracker/update/([^/]*)", GetLatestForTicker),
    ("/api/stock_tracker/update", RunPriceSyncTask),
], debug=True))
