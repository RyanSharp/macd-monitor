'''
Calculate MACD and EMAs
'''
import datetime
import json
import httplib2
import logging


_CLOSE_INDEX = 4
_DATE_INDEX = 0
_DATE_FORMAT = "%Y-%m-%d"


def calculate_ema(curr_val, prev_ema, ema_length):
    '''
    Calculates today's EMA value based on previous EMA and current value
    '''
    k = 2 / (ema_length + 1)
    return (curr_val * k) + (prev_ema * (1 - k))


def get_seed_data_for_ticker(ticker):
    '''
    Gets historical data for a quote
    '''
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
        closing_prices.append(
            [data[_CLOSE_INDEX], datetime.datetime.strptime(data[_DATE_INDEX], _DATE_FORMAT)])
    return closing_prices


def get_quote_for_ticker(ticker):
    '''
    Pulls latest stock quote from Yahoo Finance for a ticker
    '''
    url = ("http://query1.finance.yahoo.com/v10/finance/quoteSummary/{0}?"
           "formatted=true&lang=en-US&region=US&"
           "modules=defaultKeyStatistics%2CfinancialData%2CcalendarEvents&"
           "corsDomain=finance.yahoo.com").format(ticker)
    http = httplib2.Http()
    _, content = http.request(url, method="GET")
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
            "date": datetime.datetime.strftime(
                key_stats.get("lastSplitDate")["fmt"], _DATE_FORMAT)
        }
    return {"price": current_price, "latest_split": split_data}
