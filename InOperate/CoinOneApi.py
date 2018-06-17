import base64
import hashlib
import hmac
import json
import time
from urllib.request import urlopen, Request
import config


def get_base_payload():
    return {
        'access_token': config.ACCESS_TOKEN,
    }


def str_2_byte(s, encode='utf-8'):
    return bytes(s, encode)


def get_encoded_payload(payload):
    payload['nonce'] = int(time.time()*1000)
    dumped_json = json.dumps(payload)
    encoded_json = base64.b64encode(str_2_byte(dumped_json))
    return encoded_json


def get_signature(encoded_payload):
    signature = hmac.new(str_2_byte(config.UPPERCASE_SECRET_KEY), encoded_payload, hashlib.sha512)
    return signature.hexdigest()


def get_response(url, payload):
    encoded_payload = get_encoded_payload(payload)
    signature = get_signature(encoded_payload)
    headers = {
        'Content-Type': 'application/json',
        'X-COINONE-PAYLOAD': encoded_payload,
        'X-COINONE-SIGNATURE': signature,
    }
    api_url = HOST + url
    req = Request(api_url, data=encoded_payload, headers=headers, method='POST')

    with urlopen(req) as res:
        data = res.read().decode('utf-8')
        return json.loads(data)

def order_coin(order_type, order_data):
    payload = get_base_payload()
    payload.update(order_data)
    
    if order_type == 'buy':
        result_set = get_response('v2/order/limit_buy/', payload)
    elif order_type == 'sell':
        result_set = get_response('v2/order/limit_sell/', payload)
    
    if result_set["errorCode"] != '0' :
        print("COIN_ONE API Response_Error, ErrorCode :", result_set["errorCode"])
        return False
    return result_set

def get_avail_account(coin_type):
    result_set = get_response('v2/account/balance/', get_base_payload())
    return round(float(result_set[coin_type]['avail']),4)

def get_balance_account(coin_type):
    result_set = get_response('v2/account/balance/', get_base_payload())
    return round(float(result_set[coin_type]['balance']),4)

def get_order_information(order_id, coin_type):
    parameters = {
        'order_id' : order_id,
        'currency' : coin_type
    }

    payload = get_base_payload()
    payload.update(parameters)

    result_set = get_response('v2/order/order_info/', payload)

    return result_set

def cancel_order(order_id, price, quantity, coin_type, is_sell):
    parameters = {
        'order_id' : order_id,
        'price' : price,
        'qty' : quantity,
        'is_ask' : is_sell,
        'currency' : coin_type
    }

    payload = get_base_payload()
    payload.update(parameters)

    result_set = get_response('v2/order/cancel', payload)

    return result_set
