from flask import Flask, request, Response
from utils.account import get_account_by_username, create_account
from utils.archive import get_chronological_archive
from utils.stock_profile import create_stock_profile, list_stock_profiles, get_stock_profile
from utils.errors import EntityAlreadyExists, QuoteNotFound
from utils.decorators import login_required
from utils.simmulate import run_historical_analysis
from config.logs import logging
import json


app = Flask(__name__)


@app.route("/test")
def test():
    return "Hello World"


@app.route("/create_superuser")
def create_superuser():
    username = "rtsharp"
    password = "thisispassword"
    try:
        create_account(username, password)
        return "Done"
    except Exception as e:
        return "{0}".format(e.message)


@app.route("/api/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        rdict = {"success": False}
        username = request.form["username"]
        password = request.form["password"]
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
@login_required()
def start_tracking_ticker(ticker):
    rdict = {"success": False}
    try:
        profile = create_stock_profile(ticker)
        rdict["success"] = True
    except EntityAlreadyExists as e:
        rdict["msg"] = e.message
    except QuoteNotFound as e:
        rdict["msg"] = e.message
    return rdict


@app.route("/api/stock_tracker/list_tickers")
@login_required()
def list_tracking_tickers():
    rdict = {"success": False}
    profiles = list_stock_profiles()
    rdict["results"] = [profile.serialize_data() for profile in profiles]
    rdict["success"] = True
    return rdict


@app.route("/api/stock_tracker/simulate/<ticker>")
@login_required()
def simulate_ticker(ticker):
    rdict = {"success": False}
    try:
        rdict["results"] = run_historical_analysis(ticker)
        rdict["success"] = True
    except Exception as e:
        logging.exception(e)
        rdict["msg"] = "{0}".format(e.message)
    return rdict


@app.route("/api/stock_tracker/archive/<ticker>/<int:last_date>")
@login_required()
def retrive_historical(ticker, last_date):
    rdict = {"success": False}
    if int(last_date) == 0:
        last_date = None
    archive = get_chronological_archive(ticker, last_date=last_date)
    rdict["results"] = [a.serialize_data() for a in archive]
    rdict["success"] = True
    return rdict


@app.route("/api/stock_tracker/<ticker>")
@login_required()
def get_profile_by_ticker(ticker):
    rdict = {"success": False}
    profile = get_stock_profile(ticker)
    if profile is not None:
        profile = profile.serialize_data()
        rdict["success"] = True
        rdict["results"] = [profile]
    else:
        rdict["msg"] = "Ticker not being tracked"
    return rdict


if __name__ == "__main__":
    app.run()
