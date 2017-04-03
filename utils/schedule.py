from pytz import timezone
import datetime


UTC_TZ = timezone("UTC")
EASTERN = timezone("US/Eastern")

_SKIP_DATES = [
    "2017-01-02",
    "2017-01-16",
    "2017-02-20",
    "2017-04-14",
    "2017-05-29",
]


def get_us_east_time():
    '''
    Returns US/East time using server time (UTC)
    '''
    now = UTC_TZ.localize(datetime.datetime.now())
    now = now.astimezone(EASTERN)
    return now


def should_sync_run():
    '''
    Checks if markets are open (holiday, before/after hours)
    '''
    now = get_us_east_time()
    if now.weekday() in [5, 6]:
        return False
    if now.hour < 5 or now.hour > 18:
        return False
    date_format = "%Y-%m-%d"
    if now.strftime(date_format) in _SKIP_DATES:
        return False
    return True


def should_analysis_run():
    '''
    Checks if markets are closed (but were open earlier that day)
    '''
    now = get_us_east_time()
    if now.weekday() in [5, 6]:
        return False
    if now.hour > 18 or now.hour < 19:
        return False
    date_format = "%Y-%m-%d"
    if now.strftime(date_format) in _SKIP_DATES:
        return False
    return True
