from flask import Flask, request, Response
from utils.account import get_account_by_username
from utils.stock_profile import create_stock_profile
from utils.errors import EntityAlreadyExists, QuoteNotFound
from utils import decorators
import httplib2
import logging
import json


@app.route("/api/login", methods=["GET", "POST"])
def user_login():
    if request.METHOD == "POST":
        rdict = {"success": False}
        username = request.POST["username"]
        password = request.POST["password"]
        account = get_account_by_username(username)
        if account.check_password(password):
            session = account.get_property("session")
            rdict["success"] = True
            response = Response(json.dumps(rdict))
            response.headers["Set-Cookie"] = "JSID={0};path=/;HttpOnly".format(session)
            return response
        else:
            rdict["msg"] = "Username/password combination failed"
        return json.dumps(rdict)
    else:
        return ("<form method='POST' action='/api/login' enctype='multipart/form-data'>"
                "<input type='text' name='username' placeholder='username' />"
                "<input type='password' name='password' placeholder='password' />"
                "<input type='submit' value='Submit' />"
                "</form>")


@app.route("/api/stock_tracker/new/<ticker>")
@decorators.login_required
def start_tracking_ticker(ticker):
    rdict = {"success": False}
    try:
        profile = create_stock_profile(ticker)
        rdict["success"] = True
    except EntityAlreadyExists as e:
        rdict["msg"] = e.message
    except QuoteNotFound as e:
        rdict["msg"] = e.message
    return json.dumps(rdict)


app = Flask(__name__)


if __name__ == "__main__":
    app.run()
