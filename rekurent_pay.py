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
user = {}  # Для записи локальны переменных в глобальную


def user_registration():
    print('Check method /user/registration...', end='')
    url = config.user_registration_rek_url
    login = '7902' + f'{random.randint(1000000, 9999999)}'
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "login": f"{login}",
        "shopToken": f"{config.shopToken}"
    }

    # Рассчет подписи
    sign_str = payload['login'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign

    headers = {
        'Content-Type': 'application/json',
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0",
    }
    request = s.post(url, data=json.dumps(payload), headers=headers).json()  # тут есть login, userToken

    if request['login'] == login:
        print('OK')
    else:
        print(f'Something wrong! url: {url}, request: {request}')
    user['login'] = login


def get_user_status(login):
    print('Check method /user/status...', end='')
    headers = {'Content-Type': 'application/json'}
    url = config.user_status_rek_url
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "login": f"{login}",
        "shopToken": f"{config.shopToken}"
    }
    # Рассчет подписи
    sign_str = payload['login'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign

    request = s.post(url, data=json.dumps(payload), headers=headers).json()

    if request['login'] == login and request['state'] == 'active':
        print('OK')
    else:
        print(f'Something wrong! url: {url}, request: {request}')
    userToken = request['userToken']
    user['userToken'] = userToken  # Записываем в глобальную переменную


def get_cards_rek(userToken):
    headers = {'Content-Type': 'application/json'}
    url = config.get_cards_rek_url
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "userToken": f"{userToken}",
        "shopToken": f"{config.shopToken}"
    }

    # Рассчет подписи
    sign_str = payload['userToken'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign

    request = s.post(url, data=json.dumps(payload), headers=headers).json()
    print('Check method /get/cards...', end='')
    cards = request['cards']
    user['cards'] = cards  # Записал в глобальную переменную
    if cards != '':
        print('OK')
    else:
        print(f'Something wrong! url: {url} request: {request}')


def card_registration(userToken):
    print('Check method /card/registration...', end='')
    headers = {'Content-Type': 'application/json'}
    url = config.card_registration_url_rek
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "userToken": f"{userToken}",
        "shopToken": f"{config.shopToken}"
    }
    # Рассчет подписи
    sign_str = payload['userToken'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign

    request = s.post(url, data=json.dumps(payload), headers=headers).json()

    registration_url = request['payUrl']
    order = registration_url.replace('https://demo-acq.bisys.ru/cardpay/card?order=', '')

    # Открываем payUrl чтоб перехватить Cookies
    s.get(registration_url, headers=headers)
    cookies = s.cookies.get_dict()

    reg_payload = {
        "form": "default",
        "operation": "checkpay",
        "order": f"{order}",
        "type": "visa",
        "pan": "4000000000000002",
        "exp": "01 21",
        "holder": "hard support",
        "secret": "123"
    }

    reg_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": f"{registration_url}",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0",
        "Cookies": f"{cookies}"
    }
    reg_url = 'https://demo-acq.bisys.ru/cardpay/api/C/rpcheck'
    reg_request = s.post(reg_url, data=reg_payload, headers=reg_headers)

    if reg_request.status_code == 200:
        print('OK')
    else:
        print(f'Something wrong! url: {url} request: {reg_request}')


def do_payment():

    url = config.do_payment_rek_url
    headers = {'Content-Type': 'application/json'}
    cardToken = user['cards'][0]['cardToken']  # Берем первую привязанную карту
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "serviceCode": f"{config.service_code}",
        "userToken": f"{user['userToken']}",
        "amount": "2500",
        "comission": "0",
        "cardToken": f"{cardToken}",  # берем первую привязанную карту
        "holdTtl": "1800",
        "properties": [
            {
                "name": "ПОЗЫВНОЙ",
                "value": f"{random.randint(10, 20)}"
            }
        ],
        "shopToken": f"{config.shopToken}"
    }
    # Рассчет подписи
    sign_str = payload['serviceCode'] + '&' + payload['userToken'] + '&' + payload['amount'] + '&' + payload['comission'] + '&' + payload['cardToken'] + '&' + payload['holdTtl'] + '&' + payload['properties'][0]['name'] + '&' + payload['properties'][0]['value'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign
    print('Check method /do/payment...', end='')
    request = (s.post(url, data=json.dumps(payload), headers=headers)).json()
    regPayNum = request['regPayNum']
    print(request)
    user['regPayNum'] = regPayNum  # Записал в глобальную переменную
    if regPayNum:
        print('OK')
    else:
        print(f'Something wrong! url: {url} request: {request}')


def confirm_pay():
    url = config.confirm_pay_rek_url
    headers = {'Content-Type': 'application/json'}
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "regPayNum": f"{user['regPayNum']}",
        "orderId": f"{random.randint(1000000, 2000000)}",
        "shopToken": f"{config.shopToken}"
    }
    # Рассчет подписи
    sign_str = payload['regPayNum'] + '&' + payload['orderId'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign

    print('Check method /provision-services/confirm...', end='')
    request = (s.post(url, data=payload, headers=headers)).json()
    print(request)


if __name__ == '__main__':
    user_registration()
    get_user_status(login=user['login'])
    card_registration(userToken=user['userToken'])
    time.sleep(4)  # Если не взять паузу, то autopays не успевает записать привязанную карту и возвращает пустой массив с картами
    get_cards_rek(userToken=user['userToken'])
    do_payment()
    time.sleep(4)
    confirm_pay()



# print(user)
# print(user['userToken'])

# card_registration('52771f3b-aa0e-42e1-855e-d0f0b80339e4')
# 'login': '79024782366'
# 'userToken': '52771f3b-aa0e-42e1-855e-d0f0b80339e4'
