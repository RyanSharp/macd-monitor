import json


def login_required():
    def wrapper(f):
        def decorator(*args, **kwargs):
            rdict = f(*args, **kwargs)
            return json.dumps(rdict)
        return decorator
    return wrapper
