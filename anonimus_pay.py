import requests
import json
import os
from .src import config
import time
import hashlib
import random
from extentions.demo_checker import app


s = requests.Session()
sert_path = 'extentions/demo_checker/src/cert.pem'
key_path = 'extentions/demo_checker/src/dec.key'
# Приватный ключ через тектсовик я вытащил из серта pem, затем командой
# "openssl rsa -in my.key_encrypted -out my.key_decrypted" (со вводом пароля) расшифровал закрытый ключ
s.cert = (sert_path, key_path)
output = ['\nCheck anonimus payment methods:\n\n']


def create_anonimus_pay():
    #print('Check method /do/payment/anonymous...', end='')
    output.append('/do/payment/anonymous...')
    url = config.anonimus_pay_url
    payload = {
        "sign": "16088965AB36DAA41E401BD948E13BBC",
        "serviceCode": f"{config.service_code}",
        "amount": "2500",
        "comission": "0",
        "properties": [
            {
                "name": "ПОЗЫВНОЙ",
                "value": f"{random.randint(10, 20)}"
            }
        ],
        "shopToken": "1a4c0d33-010c-4365-9c65-4c7f9bb415d5"
    }
    # Рассчет подписи
    sign_str = payload['serviceCode'] + '&' + payload['amount'] + '&' + payload['comission'] + '&' + payload['properties'][0]['name'] + '&' + payload['properties'][0]['value'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign
    headers = {
        'Content-Type': 'application/json',
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0",
    }
    r = s.post(url, data=json.dumps(payload), headers=headers)
    request = r.json()

    try:
        sign = request['sign']
        shopToken = request['shopToken']
        regPayNum = request['regPayNum']
        payUrl = request['payUrl']
        methodType = request['methodType']
    except KeyError:
        #print(f'Something wrong! Key Error. Url: {url}, request: {request}')
        output.append(f'Something wrong! Except Key Error. Url: {url}, request: {request}\n')

    #print(f'sign: {sign}\nshopToken: {shopToken}\nregPayNum: {regPayNum}\npayurl: {payurl}\nmethodType: {methodType}')
    if sign != '' and methodType == 'GET' and shopToken != '' and 'https://demo-acq.bisys.ru/cardpay/card?order=' in payUrl and regPayNum != '':
        #print('OK')
        output.append('OK\n')
    else:
        #print(f'Something wrong!\nrequest_status_code: {r.status_code}\nrequest: {request}')
        output.append(f'Something wrong!\nrequest_status_code: {r.status_code}\nrequest: {request}\n')
    # Открываем полученную ссылку, чтоб перехватить Cookies
    s.get(payUrl, headers=headers)
    cookies = s.cookies.get_dict()
    return payUrl, regPayNum, cookies


def payment_created_pay():
    #print('Trying to payment created pay')
    output.append('Trying to payment created pay...\n')
    created_pay_data = create_anonimus_pay()
    payUrl = created_pay_data[0]
    regPayNum = created_pay_data[1]
    cookies = created_pay_data[2]
    order = payUrl.replace('https://demo-acq.bisys.ru/cardpay/card?order=', '')
    payload = {
        "form": "default",
        "operation": "pay",
        "order": f"{order}",
        "type": "visa",
        "pan": "4000000000000002",
        "exp": "01 21",
        "holder": "hard support",
        "secret": "123"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": f"{payUrl}",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0",
        "Cookies": f"{cookies}"
    }

    url = config.acq_pay_url
    s.post(url, data=payload, headers=headers)

    check_pay_status(regPayNum)


def check_pay_status(regPayNum):
    url = config.payment_state_url
    #print('Check payment state...', end='')
    output.append('Check payment state...')
    payload = {
        "sign": "AE13A1572E1A3594A0A956EB751D7F6D",
        "regPayNum": f"{regPayNum}",
        "shopToken": f"{config.shopToken}"
    }
    headers = {
        "Content-Type": "application/json"
    }
    sign_str = payload['regPayNum'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign

    r = s.post(url, data=json.dumps(payload), headers=headers)
    request = r.json()
    payment_state = request['state']
    if payment_state == 'payed':
        #print('OK\n')
        output.append('OK\n')
    elif payment_state == 'created':
        output.append(f'Payment state: {payment_state}. Retry...\n')
        #print(f'Payment state: {payment_state}. Retry...')
        time.sleep(10)
        check_pay_status(regPayNum)
    else:
        output.append(f'Something wrong! payment state: {payment_state}\n')
        #print(f'Something wrong! payment state: {payment_state}')



