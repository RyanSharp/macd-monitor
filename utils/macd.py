'''
Calculate MACD and EMAs
'''
from config.logs import logging
import datetime
import json
import urllib2


_CLOSE_INDEX = 6
_DATE_INDEX = 0
_DATE_FORMAT = "%Y-%m-%d"


def calculate_ema(curr_val, prev_ema, ema_length):
    '''
    Calculates today's EMA value based on previous EMA and current value
    '''
    k = float(2) / (ema_length + 1)
    return (curr_val * k) + (prev_ema * (1 - k))


def get_seed_data_for_ticker(ticker):
    '''
    Gets historical data for a quote
    '''
    today = datetime.datetime.now()
    quote = get_quote_for_ticker(ticker)
    cutoff = datetime.datetime.strptime("2015-01-01", _DATE_FORMAT)
    # if quote["latest_split"]["date"] is not None:
    #     if quote["latest_split"]["date"] > cutoff:
    #         cutoff = quote["latest_split"]["date"]
    url = ("http://chart.finance.yahoo.com/table.csv?"
           "s={0}&a={1}&b={2}&c={3}&d={4}&e={5}&f={6}&g=d&ignore=.csv")\
          .format(ticker, cutoff.month-1, cutoff.day, cutoff.year,
                  today.month-1, today.day, today.year)
    content = urllib2.urlopen(url).read()
    rows = reversed(content.split("\n")[1:-1])
    closing_prices = []
    for row in rows:
        data = row.split(",")
        closing_prices.append(
            [float(data[_CLOSE_INDEX]),
             datetime.datetime.strptime(data[_DATE_INDEX], _DATE_FORMAT)])
    return closing_prices


def get_quote_for_ticker(ticker):
    '''
    Pulls latest stock quote from Yahoo Finance for a ticker
    '''
    url = ("http://query1.finance.yahoo.com/v10/finance/quoteSummary/{0}?"
           "formatted=true&lang=en-US&region=US&"
           "modules=defaultKeyStatistics%2CfinancialData%2CcalendarEvents&"
           "corsDomain=finance.yahoo.com").format(ticker)
    content = urllib2.urlopen(url).read()
    content = json.loads(content)
    if "quoteSummary" in content and "result" in content["quoteSummary"]\
            and content["quoteSummary"]["result"] is not None:
        return parse_yahoo_finance_quote(content["quoteSummary"]["result"][0])
    return None


def parse_yahoo_finance_quote(data):
    '''
    Extracts relevant information from yahoo finance stock summary
    '''
    split_data = None
    key_stats = data["defaultKeyStatistics"]
    fin_data = data["financialData"]
    current_price = fin_data["currentPrice"]["raw"]
    factor = key_stats.get("lastSplitFactor")
    if factor is not None:
        factor = factor.split("/")
        factor = int(factor[0]) / float(factor[1])
        split_data = {
            "ratio": factor,
            "date": datetime.datetime.strptime(
                key_stats.get("lastSplitDate")["fmt"], _DATE_FORMAT)
        }
    return {"price": current_price, "latest_split": split_data}


def calculate_health_factor(recent_data):
    '''
    Calculates averaged daily growth for different intervals
    '''
    data_length = len(recent_data) - 1
    recent_diff = map(lambda x, y: x-y, recent_data[:-1], recent_data[1:])
    avg_growth_rates = {}
    for i in xrange(data_length):
        avg_growth_rates[str(data_length-i) + "d"] = sum(recent_diff[i:])/(data_length - i)
    return avg_growth_rates
