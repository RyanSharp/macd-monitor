# MACD-Monitor
## Purpose
Tracking the momentum and short term trends of financial assets.  Evaluates the MACD lines for large numbers of stocks to identify potential for short term buys.

## How it works
The application is built using a combination of Flask and MongoDB.  Stock data is pulled from Yahoo finance.

I wrote a custom meta class for handling Mongo datastructures within the flask application, more to see if I could than anything else.  It does offer some structure to the mongo backend and simplifies the creation of new models and their integration with the rest of the application, but is totally unecessary and not necessarily a shining example of best practices :P.

Through the Flask endpoints, users can register new tickers to be tracked by the application.  When submitted, the app first verifies that the ticker is in use and has data by querying against Yahoo finance, then it pulls the historical data and runs through each closing price to build a profile for that stock (also calculating EMA values and a 'momentum analysis' along the way).

Once a ticker is registered with the application, it will begin pulling data for those tickers on a daily basis.  The app is programmed to skip weekends and skip the task beat for before and after market hours, but the user will be required to update the application with irregular holiday dates to skip.  This will need to be done in the `/utils/schedule.py` file.

## Deployment
Code base is meant for deployment on an Ubuntu 16.04 server, included in the repository are the systemd config files for services to run the celery tasks, celery beat, and gunicorn application.  Also included is an nginx config file for opening up access to the gunicorn application to the network.

User is required to install nginx, mongodb, python-dev.  Also included is `requirements.txt`, which must be installed using `pip install -t lib -r requirements.txt`.  Inside the `lib` folder, include the following code to the `__init__.py` file in order to add `lib` to the root path for the project.
```
import os
import sys
sys.path.append(os.path.dirname(__file__))
```
The application logs app to `/var/log/applog.log` and `/var/log/customtasks.log` so the user that will own the application (in my scripts, I use the user `appadmin`) must own these files, as well as the directory where the code lives (in my case `/home/appadmin/macd-monitor`).
