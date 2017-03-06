from google.appengine.ext import ndb


class StockQuote(ndb.Model):
    price = ndb.FloatProperty()
    date = ndb.DateProperty()


class ExponentialMovingAverageValue(ndb.Model):
    value = ndb.FloatProperty()


class StockProfile(ndb.Model):
    ticker = ndb.StringProperty()
    points = ndb.StructuredProperty(StockQuote, repeated=True)
    ema26 = ndb.FloatProperty(ExponentialMovingAverageValue, repeated=True)
    ema12 = ndb.FloatProperty(ExponentialMovingAverageValue, repeated=True)
    macd_ema9 = ndb.FloatProperty(ExponentialMovingAverageValue, repeated=True)


class ArchivedQuote(ndb.Model):
    ticker = ndb.StringProperty()
    price = ndb.FloatProperty()
    date = ndb.DateProperty()
