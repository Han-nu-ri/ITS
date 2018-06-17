import json
import requests
import urllib
import datetime
import time 
import os
from slackclient import SlackClient
import config

# send message to the channel
def send_message_to_slack(message):
   # get slack client
   slack_lient =  SlackClient(config.BOT_TOKEN)
   # send slack message
   slack_lient.api_call (
      "chat.postMessage",
      channel = config.CHANNEL,
      text = message
)
