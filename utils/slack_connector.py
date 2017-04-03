'''
    Send updates to people using Slack
'''
from config.app_config import _SLACK_WEBHOOK_URL
import httplib2
import json


def send_message(message):
    '''
        Sends message to Webhook provided in config.app_config
        Input should be str or unicode
    '''
    if not isinstance(message, (str, unicode)):
        raise ValueError("Invalid type for Slack Message")
    http = httplib2.Http()
    message = {"text": message}
    http.request(_SLACK_WEBHOOK_URL,
                 method="POST",
                 body=json.dumps(message),
                 headers={"Content-Type": "application/json"})
