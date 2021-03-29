import requests
import json
from src import config
import time
import hashlib
import random
from loguru import logger

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


s = requests.Session()
sert_path = 'src/cert.pem'
key_path = 'src/dec.key'
# Сам сертификат выдает support
# Приватный ключ через тектсовик вытащил из серта pem, затем командой
# "openssl rsa -in my.key_encrypted -out my.key_decrypted" (со вводом пароля) расшифровал закрытый ключ
s.cert = (sert_path, key_path)
user = {'retry': 0}  # Для записи локальных переменных в глобальную


def create_anonimus_pay():
    print('\nCheck anonimus payment methods:\n')
    print('/do/payment/anonymous...', end='')
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
    #logger.info(f'r.text: {r.text}')

    if r.status_code == 200:
        request = r.json()
        try:
            user['sign'] = request['sign']
            user['shopToken'] = request['shopToken']
            user['regPayNum'] = request['regPayNum']
            user['payUrl'] = request['payUrl']
            user['methodType'] = request['methodType']

            # Открываем полученную ссылку, чтоб перехватить Cookies
            s.get(user['payUrl'], headers=headers)
            user['cookies'] = s.cookies.get_dict()

            if user['sign'] and user['methodType'] == 'GET' and user['shopToken'] and 'https://demo-acq.bisys.ru/cardpay/card?order=' in user['payUrl'] and user['regPayNum']:
                print('OK')
            else:
                print(f'Something wrong!\nrequest_status_code: {r.status_code}\nrequest: {request}')
        except KeyError:
            print(f'Something wrong! Key Error. Url: {url}, request: {request}')

        # print(f'sign: {sign}\nshopToken: {shopToken}\nregPayNum: {regPayNum}\npayurl: {payurl}\nmethodType: {methodType}')
    else:
        print(f'\ncreate_anonimus_pay: http error. request status code: {r.status_code}')


def payment_created_pay():
    #logger.info('Trying to payment created pay')
    print('Trying to payment created pay...\nSend a POST request...', end='')
    order = user['payUrl'].replace('https://demo-acq.bisys.ru/cardpay/card?order=', '')
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
        "Referer": f"{user['payUrl']}",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0",
        "Cookies": f"{user['cookies']}"
    }

    url = config.acq_pay_url
    r = s.post(url, data=payload, headers=headers)
    if r.status_code == 200:
        print('Response code == 200 OK')
    else:
        print(f'Something wrong!\nrequest_status_code: {r.status_code}\nrequest_text: {r.text}\n')


def check_pay_status():
    url = config.payment_state_url
    #logger.info('Check payment state...')
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
        print('OK\n')
    elif payment_state == 'created':
        if user['retry'] <= 3:
            print(f'Payment state: {payment_state}. Retry...')
            time.sleep(5)
            user['retry'] += 1
            check_pay_status()
        else:
            print(f"Платеж {user['regPayNum']} висит в статусе 'created'")
    else:
        print(f'Something wrong! payment state: {payment_state}, response: {request}')

