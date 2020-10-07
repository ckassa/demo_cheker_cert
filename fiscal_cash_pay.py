from src import config
import json
import hashlib
import random
import requests
import os
import time

s = requests.Session()
sert_path = 'src/cert.pem'
key_path = 'src/dec.key'
# Приватный ключ через тектсовик я вытащил из серта pem, затем командой
# "openssl rsa -in my.key_encrypted -out my.key_decrypted" (со вводом пароля) расшифровал закрытый ключ
s.cert = (sert_path, key_path)
user = {}


def create_anonimus_pay():
    print('Check method /do/payment/anonymous...', end='')
    url = config.anonimus_pay_url
    payload = {
        "sign": "16088965AB36DAA41E401BD948E13BBC",
        "serviceCode": "15636-15727-1",
        "amount": "2500",
        "comission": "0",
        "payType": "fiscalCash",
        "properties": [
            {
                "name": "ТЕЛЕФОН",
                "value": f"{random.randint(9000000000, 9999999999)}"
            },
            {
                "name": "ФИО",
                "value": "Тестов Тест Тестович"
            },
            {
                "name": "АДРЕС",
                "value": "Тестовый адрес"
            }
        ],
        "shopToken": "1a4c0d33-010c-4365-9c65-4c7f9bb415d5"
    }
    # Рассчет подписи
    sign_str = payload['serviceCode'] + '&' + payload['amount'] + '&' + payload['comission'] + '&' + payload['payType'] + '&' + payload['properties'][0]['name'] + '&' + payload['properties'][0]['value'] + '&' + payload['properties'][1]['name'] + '&' + payload['properties'][1]['value'] + '&' + payload['properties'][2]['name'] + '&' + payload['properties'][2]['value'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign

    headers = {
        'Content-Type': 'application/json',
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0",
    }
    r = s.post(url, data=json.dumps(payload), headers=headers)
    request = r.json()
    regPayNum = request['regPayNum']
    user['regPayNum'] = regPayNum
    if regPayNum != '':
        print('OK')
    else:
        print(f'Something wrong! Key Error. Url: {url}, request: {request}')


def check_pay_status():
    url = config.payment_state_url
    print('Check payment state...', end='')
    payload = {
        "sign": "AE13A1572E1A3594A0A956EB751D7F6D",
        "regPayNum": f"{user['regPayNum']}",
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
        print('OK')
    elif payment_state == 'created':
        print(f' Warn: Payment state: {payment_state}. Retry...')
        time.sleep(5)
        check_pay_status()
    else:
        print(f'Something wrong! payment state: {payment_state} Request: {request}')


def get_fiscal_check():
    url = config.fiscal_check_url
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "sign": "AE13A1572E1A3594A0A956EB751D7F6D",
        "regPayNum": f"{user['regPayNum']}",
        "shopToken": f"{config.shopToken}"
    }
    # Рассчет подписи
    sign_str = payload['regPayNum'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign
    print('Check method /receipt-fiscal...', end='')
    r = s.post(url, data=json.dumps(payload), headers=headers)
    request = r.json()
    fiscal_url = request['fiscalUrl']
    if fiscal_url:
        print(f'OK')
    else:
        print(f'Something wrong! Key Error. Url: {url}, request: {request}')

