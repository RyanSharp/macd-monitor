'''
Calculate MACD and EMAs
'''
from entities import ArchivedQuote
import datetime
import json
import httplib2
import logging


def calculate_ema(curr_val, prev_ema, ema_length):
    '''
    Calculates today's EMA value based on previous EMA and current value
    '''
    k = 2 / (ema_length + 1)
    return (curr_val * k) + (prev_ema * (1 - k))


def calibrate_ema(data_set, ema_length):
    if len(data_set) < 100:
        raise Exception("EMA requires at least 100 datapoints to calibrate")
    curr_index = 1
    curr_ema = None
    prev_ema = data_set[0]
    while curr_index < len(data_set):
        curr_ema = calculate_ema(data_set[curr_index], prev_ema, ema_length)
        prev_ema = curr_ema
    return curr_ema


_CLOSE_INDEX = 4
_DATE_INDEX = 0
_DATE_FORMAT = "%Y-%m-%d"

def get_seed_data_for_ticker(ticker):
    today = datetime.datetime.now()
    url = ("http://chart.finance.yahoo.com/table.csv?"
           "s={0}&a=1&b=1&c=2016&d={1}&e={2}&f={3}&g=d&ignore=.csv")\
          .format(ticker, today.day, today.month, today.year)
    http = httplib2.Http()
    _, content = http.request(url, method="GET")
    rows = reversed(content.split("\n")[1:])
    closing_prices = []
    for row in rows:
        data = row.split(",")
        closing_prices.append([data[_CLOSE_INDEX], data[_DATE_INDEX]])
        quote = ArchivedQuote(id="{0}_{1}".format(ticker, data[_DATE_INDEX]),
                              ticker=ticker,
                              price=data[_CLOSE_INDEX],
                              date=datetime.datetime.strptime(data[_DATE_INDEX], _DATE_FORMAT))
        quote.put()
    return closing_prices


def calibrate_macd(points):
    if len(points) < 126:
        raise Exception("MACD cannot be calibrated with less than 126 points")
    ema26_dataset = points[:126]
    ema12_dataset = points[(26-12):126]
    remaining_dataset = points[126:]
    ema26 = calibrate_ema([x[0] for x in ema26_dataset], 26)
    ema12 = calibrate_ema([x[0] for x in ema12_dataset], 12)
    return ema26, ema12, remaining_dataset


def get_quote_for_ticker(ticker):
    url = ("http://query1.finance.yahoo.com/v10/finance/quoteSummary/{0}?"
           "formatted=true&lang=en-US&region=US&"
           "modules=defaultKeyStatistics%2CfinancialData%2CcalendarEvents&"
           "corsDomain=finance.yahoo.com").format(ticker)
    http = httplib2.Http()
    _, content = http.request(url, method="GET")
    content = json.loads(content)
    try:
        return content["quoteSummary"]["result"][0]
    except Exception as e:
        logging.exception(e)
    return None
