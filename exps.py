import requests
import json
import os
from src import config
import time
import hashlib

s = requests.Session()
sert_path = 'src' + os.sep + 'cert.pem'
key_path = 'src' + os.sep + 'dec.key'
# Приватный ключ через тектсовик я вытащил из серта pem, затем командой
# "openssl rsa -in my.key_encrypted -out my.key_decrypted" (со вводом пароля) расшифровал закрытый ключ
s.cert = (sert_path, key_path)


def create_anonimus_pay():
    try:
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
                    "value": "11"
                }
            ],
            "shopToken": "1a4c0d33-010c-4365-9c65-4c7f9bb415d5"
        }
        headers = {'Content-Type': 'application/json'}
        r = s.post(url, data=json.dumps(payload), headers=headers)
        request = r.json()

        sign = request['sign']
        shopToken = request['shopToken']
        regPayNum = request['regPayNum']
        payUrl = request['payUrl']
        methodType = request['methodType']

        #print(f'sign: {sign}\nshopToken: {shopToken}\nregPayNum: {regPayNum}\npayurl: {payurl}\nmethodType: {methodType}')
        if sign != '' and methodType == 'GET' and shopToken != '' and 'https://demo-acq.bisys.ru/cardpay/card?order=' in payUrl and regPayNum != '':
            print('OK')
        else:
            print(f'Something wrong!\nrequest_status_code: {r.status_code}\nrequest: {request}')
        print(f'payurl: {payUrl}')
        return payUrl, regPayNum

    except KeyError:
        print(f'KeyERROR. url: {url}\nrequest: {request}')


def payment_created_pay():
    created_pay_data = create_anonimus_pay()
    payUrl = created_pay_data[0]
    regPayNum = created_pay_data[1]
    order = payUrl.replace('https://demo-acq.bisys.ru/cardpay/card?order=', '')
    #proxy = {'https': 'https://127.0.0.1:8080/'}
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
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0"
    }
    url = 'https://demo-acq.bisys.ru/cardpay/api/C/pay'
    r = s.post(url, data=payload, headers=headers)
    #print(f'headers: {r.headers}')
    print(r.status_code)
    check_pay_status(regPayNum)


def check_pay_status(regPayNum):
    url = config.payment_state_url
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
    print(request)


if __name__ == '__main__':
    payment_created_pay()

