import json


def login_required():
    def wrapper(f):
        def func2_wrap(*args, **kwargs):
            rdict = f(*args, **kwargs)
            return json.dumps(rdict)
        return func2_wrap
    return wrapper
