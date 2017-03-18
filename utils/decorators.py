from functools import wraps
import json


def login_required():
    def wrapper(f):
        @wraps(f)
        def func_wrap(*args, **kwargs):
            rdict = f(*args, **kwargs)
            return json.dumps(rdict)
        return func_wrap
    return wrapper
