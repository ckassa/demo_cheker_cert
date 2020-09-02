import requests
import json
import os
from src import config
import time
import hashlib
import random

s = requests.Session()
sert_path = 'src' + os.sep + 'cert.pem'
key_path = 'src' + os.sep + 'dec.key'
# Приватный ключ через тектсовик я вытащил из серта pem, затем командой
# "openssl rsa -in my.key_encrypted -out my.key_decrypted" (со вводом пароля) расшифровал закрытый ключ
s.cert = (sert_path, key_path)


def create_anonimus_pay():
    print('Check method "/do/payment/anonymous"...', end='')
    url = config.anonimus_pay_url
    payload = {
        "sign": "16088965AB36DAA41E401BD948E13BBC",
        "serviceCode": "1000-13864-2",
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
    sign_str = payload['serviceCode'] + '&' + payload['amount'] + '&' + payload['comission'] + '&' + payload['properties'][0]['name'] + '&' + payload['properties'][0]['value'] + '&' + payload['shopToken'] +  '&' + config.sec_key
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
        print(f'Something wrong! Key Error. Url: {url}, request: {request}')

    #print(f'sign: {sign}\nshopToken: {shopToken}\nregPayNum: {regPayNum}\npayurl: {payurl}\nmethodType: {methodType}')
    if sign != '' and methodType == 'GET' and shopToken != '' and 'https://demo-acq.bisys.ru/cardpay/card?order=' in payUrl and regPayNum != '':
        print('OK')
    else:
        print(f'Something wrong!\nrequest_status_code: {r.status_code}\nrequest: {request}')
    # Открываем полученную ссылку, чтоб перехватить Cookies
    s.get(payUrl, headers=headers)
    cookies = s.cookies.get_dict()
    return payUrl, regPayNum, cookies


def payment_created_pay():
    print('Payment created pay...')
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
    print('Check payment state...', end='')
    payload = {
        "sign": "AE13A1572E1A3594A0A956EB751D7F6D",
        "regPayNum": f"{regPayNum}",
        "shopToken": "1a4c0d33-010c-4365-9c65-4c7f9bb415d5"
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
    global try_number
    try_number = 0
    if payment_state == 'payed':
        print('OK')
    elif payment_state == 'created' and try_number <= 10:
        try_number += 1
        print(f'Payment state: {payment_state}. Try number {try_number}')
        time.sleep(10)
        check_pay_status(regPayNum)
    else:
        print(f'Something wrong! payment state: {payment_state}')