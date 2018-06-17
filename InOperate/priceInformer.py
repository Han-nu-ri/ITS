import json
import requests
import urllib
import datetime
import time
import pymysql 
import os
from Slack import send_message_to_slack

insert_count_after_sent_message_to_slack = 0
while True:
    try :
        url_ticker = urllib.request.urlopen('https://api.coinone.co.kr/ticker/?currency=all')

        read_ticker = url_ticker.read()
        json_ticker = json.loads(read_ticker)

        current_time_stamp = datetime.datetime.fromtimestamp((time.time() + 32400)).strftime('%Y-%m-%d %H:%M:%S')
        btc = int(json_ticker['btc']['last'])
        xrp = int(json_ticker['xrp']['last'])
        eth = int(json_ticker['eth']['last'])
        
        connection = pymysql.connect(host = 'localhost', user = 'root', password = 'root', db = 'coin_info')
        cursor = connection.cursor()
        sql = "insert into coin_price values ('%s', '%d', '%d', '%d')" % (current_time_stamp, btc, xrp, eth)
        cursor.execute(sql)
        connection.commit()
        connection.close()

        insert_count_after_sent_message_to_slack = insert_count_after_sent_message_to_slack + 1
        if insert_count_after_sent_message_to_slack == 30 :
            message = """Current TimeStamp : %s, BTC : %d, XRP : %d, ETH : %d""" % (current_time_stamp, btc, xrp, eth)
            send_message_to_slack(message)
            insert_count_after_sent_message_to_slack = 0
    except Exception as exception:
        print("Exception Is Occurred, ", exception)
        send_message_to_slack(exception)
    finally:
        time.sleep(60)
