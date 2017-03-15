from models.classes import ArchivedUpdate
from config.database import ARCHIVED_UPDATES_COLLECTION
from models.database import get_collection


def get_or_create_archive(symbol, date_int):
    '''
    Attempts to find archived update for date and symbol
    '''
    collection = get_collection(ARCHIVED_UPDATES_COLLECTION)
    archived_update = collection.find_one({"ticker": symbol, "date": date_int})
    if archived_update is not None:
        return ArchivedUpdate(archived_update)
    return ArchivedUpdate({"ticker": symbol, "date": date_int})
