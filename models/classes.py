from models.base import Attribute, BaseClass
from utils.macd import calculate_ema, calculate_health_factor
from config.database import ACCOUNT_COLLECTION, HOLDING_PROFILES_COLLECTION, ARCHIVED_UPDATES_COLLECTION
import hashlib


class Account(BaseClass):
    def __init__(self, data):
        BaseClass.__init__(self, data)
        self.properties = [
            Attribute("username", [str, unicode], required=True, val=data.get("username")),
            Attribute("salt", [str, unicode], required=True, val=data.get("salt")),
            Attribute("hashed_pw", [str, unicode], required=True, val=data.get("hashed_pw")),
            Attribute("session", [str, unicode], required=False, val=data.get("session")),
        ]
        self.collection = ACCOUNT_COLLECTION

    def _get_properties(self):
        return self.properties

    def _get_collection(self):
        return self.collection

    def check_password(self, password):
        password = "{0}{1}".format(password, self.get_property("salt"))
        password = hashlib.sha512(password).hexdigest()
        return password == self.get_property("hashed_pw")


class ArchivedUpdate(BaseClass):
    def __init__(self, data):
        BaseClass.__init__(self, data)
        self.properties = [
            Attribute("ticker", [str, unicode], required=True, val=data.get("ticker")),
            Attribute("date", [int], required=True, val=data.get("date")),
            Attribute("price", [float], required=True, val=data.get("price")),
            Attribute("ema26", [float], required=True, val=data.get("ema26")),
            Attribute("ema12", [float], required=True, val=data.get("ema12")),
            Attribute("macd_ema9", [float], required=False, val=data.get("macd_ema9")),
            Attribute("health_factor", [dict], required=False, val=data.get("health_factor")),
        ]
        self.collection = ARCHIVED_UPDATES_COLLECTION

    def _get_properties(self):
        return self.properties

    def _get_collection(self):
        return self.collection


class DailyUpdate(BaseClass):
    def __init__(self, data):
        BaseClass.__init__(self, data)
        self.properties = [
            Attribute("date", [int], required=True, val=data.get("date")),
            Attribute("price", [float], required=True, val=data.get("price")),
            Attribute("ema26", [float], required=True, val=data.get("ema26")),
            Attribute("ema12", [float], required=True, val=data.get("ema12")),
            Attribute("macd_ema9", [float], required=False, val=data.get("macd_ema9")),
        ]

    def _get_properties(self):
        return self.properties

    def _get_collection(self):
        return None


class HoldingProfile(BaseClass):
    def __init__(self, data):
        BaseClass.__init__(self, data)
        self.properties = [
            Attribute("ticker", [str, unicode], required=True, val=data.get("ticker")),
            Attribute("recent_data", [DailyUpdate], islist=True, val=data.get("recent_data", [])),
            Attribute("total_data", [int], required=True, val=data.get("total_data", 0)),
            Attribute("last_split", [int], required=False, val=data.get("last_split")),
        ]
        self.collection = HOLDING_PROFILES_COLLECTION

    def _get_properties(self):
        return self.properties

    def _get_collection(self):
        return self.collection

    def update_profile(self, price, for_date, archived_update):
        attribute = self.get_property("recent_data")
        recent_data = attribute.get_val()
        overwrite_latest = False
        if recent_data and len(recent_data) > 0:
            last_update = recent_data[-1]
            if last_update.get_property("date").get_val() == for_date:
                overwrite_latest = True
                last_update = recent_data[-2]
            update_data = dict(
                date=for_date,
                price=price,
                ema26=calculate_ema(price, last_update.get_property("ema26").get_val(), 26),
                ema12=calculate_ema(price, last_update.get_property("ema12").get_val(), 12))
            if last_update.get_property("macd_ema9").get_val() is None:
                update_data["macd_ema9"] = update_data["ema12"] - update_data["ema26"]
            else:
                update_data["macd_ema9"] =\
                    calculate_ema(update_data["ema12"] - update_data["ema26"],
                                  last_update.get_property("macd_ema9").get_val(), 9)
            update = DailyUpdate(update_data)
            if overwrite_latest:
                attribute.apply_transaction("$pop", value=1)
                attribute.apply_transaction("$push", value=update)
            else:
                attribute.apply_transaction("$push", update)
                if len(recent_data) > 100:
                    attribute.apply_transaction("$pop", value=-1)
        else:
            update = DailyUpdate(dict(date=for_date,
                                      price=price,
                                      ema26=price,
                                      ema12=price,
                                      macd_ema9=None))
            attribute.apply_transaction("$push", value=update)
        self.get_property("total_data").apply_transaction("$inc", value=1)
        update_data = update.serialize_data()
        update_data["ticker"] = self.get_property("ticker").get_val()
        if self.get_property("total_data").get_val() > 110:
            update_data["health_factor"] =\
                calculate_health_factor(
                    [x.get_property("macd_ema9").get_val() for x in
                     self.get_property("recent_data").get_val()[-11:]])
        archived_update.get_property("price").apply_transaction("$set", value=price)
        archived_update.get_property("ema26")\
            .apply_transaction("$set", value=update_data.get("ema26"))
        archived_update.get_property("ema12")\
            .apply_transaction("$set", value=update_data.get("ema12"))
        archived_update.get_property("macd_ema9")\
            .apply_transaction("$set", value=update_data.get("macd_ema9"))
        archived_update.get_property("health_factor")\
            .apply_transaction("$set", value=update_data.get("health_factor"))
        archived_update.commit()
