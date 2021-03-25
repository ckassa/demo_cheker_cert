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
# Приватный ключ через тектсовик я вытащил из серта pem, затем командой
# "openssl rsa -in my.key_encrypted -out my.key_decrypted" (со вводом пароля) расшифровал закрытый ключ
s.cert = (sert_path, key_path)
user = {}  # Для записи локальных переменных в глобальную
json_headers = {'Content-Type': 'application/json'}


def user_registration():
    print('\nCheck rekurrent payment methods:\n')
    print('/user/registration...', end='')
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

    r = s.post(url, data=json.dumps(payload), headers=json_headers)

    if r.status_code == 200:
        request = r.json()
        try:
            print('OK')
            user['login'] = request['login']
        except KeyError:
            print(f'Something wrong! url: {url}, request: {request}')
    else:
        print(f'\nuser_registration: http error. request status code: {r.status_code}')


def get_user_status():
    print('/user/status...', end='')
    url = config.user_status_rek_url
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "login": f"{user['login']}",
        "shopToken": f"{config.shopToken}"
    }
    # Рассчет подписи
    sign_str = payload['login'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign

    request = s.post(url, data=json.dumps(payload), headers=json_headers).json()

    if request['state'] == 'active':
        print('OK')
    else:
        print(f'Something wrong! url: {url}, request: {request}')
    userToken = request['userToken']
    user['userToken'] = userToken  # Записываем в глобальную переменную


def get_cards_rek():
    url = config.get_cards_rek_url
    print('/get/cards...', end='')
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "userToken": f"{user['userToken']}",
        "shopToken": f"{config.shopToken}"
    }

    # Рассчет подписи
    sign_str = payload['userToken'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign

    request = s.post(url, data=json.dumps(payload), headers=json_headers).json()
    #print('Check method /get/cards...', end='')
    cards = request['cards']
    user['cards'] = cards  # Записал в глобальную переменную
    if cards:
        print('OK')
    else:
        print(f'Something wrong! url: {url} request: {request}')


def card_registration():
    print('/card/registration...', end='')
    url = config.card_registration_url_rek
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "userToken": f"{user['userToken']}",
        "shopToken": f"{config.shopToken}"
    }
    # Рассчет подписи
    sign_str = payload['userToken'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign

    request = s.post(url, data=json.dumps(payload), headers=json_headers).json()

    registration_url = request['payUrl']
    order = registration_url.replace('https://demo-acq.bisys.ru/cardpay/card?order=', '')

    # Открываем payUrl чтоб перехватить Cookies
    s.get(registration_url, headers=json_headers)
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
        #print(f'request: {reg_request.text}')
    else:
        print(f'Something wrong! url: {url} request: {reg_request}')


def do_payment():

    url = config.do_payment_rek_url
    print('/do/payment...', end='')
    try:
        cardToken = user['cards'][0]['cardToken']  # Берем первую привязанную карту
    except IndexError:
        print('IndexError... No cards. Start method /card/registration...')
        card_registration()  # пробуем повторно зарегать карту
        try:
            cardToken = user['cards'][0]['cardToken']
        except IndexError:
            print('IndexError... No cards. Stop method.\n')
            return
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "serviceCode": f"{config.service_code}",
        "userToken": f"{user['userToken']}",
        "amount": "2500",
        "comission": "0",
        "cardToken": f"{cardToken}",  # берем первую привязанную карту
        "holdTtl": "345600",
        "properties": [
            {
                "name": "ПОЗЫВНОЙ",
                "value": f"{random.randint(10, 20)}"
            }
        ],
        "shopToken": f"{config.shopToken}"
    }
    # Рассчет подписи
    sign_str = payload['serviceCode'] + '&' + payload['userToken'] + '&' + payload['amount'] + '&' + \
               payload['comission'] + '&' + payload['cardToken'] + '&' + payload['holdTtl'] + '&' + \
               payload['properties'][0]['name'] + '&' + payload['properties'][0]['value'] + '&' + \
               payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign
    #print('Check method /do/payment...', end='')
    request = (s.post(url, data=json.dumps(payload), headers=json_headers)).json()
    regPayNum = request['regPayNum']

    user['regPayNum'] = regPayNum  # Записал в глобальную переменную
    if regPayNum:
        print('OK')
    else:
        print(f'Something wrong! url: {url} request: {request}')


def confirm_pay():
    url = config.confirm_pay_rek_url
    print('/provision-services/confirm...', end='')
    try:
        regPayNum = user['regPayNum']
    except KeyError:
        print('No regPayNum. Stop Method\n')
        return
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "regPayNum": f"{regPayNum}",
        "orderId": f"{random.randint(1000000, 2000000)}",
        "shopToken": f"{config.shopToken}"
    }
    # Рассчет подписи
    sign_str = payload['regPayNum'] + '&' + payload['orderId'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign

    #print('Check method /provision-services/confirm...', end='')
    request = (s.post(url, data=json.dumps(payload), headers=json_headers)).json()
    result = request['resultState']
    if result == 'success':
        user['payment_state'] = result
        print('OK')
    else:
        print(f'Something wrong! url: {url} request: {request}')


def get_pay_state():
    url = config.get_pay_state_url
    print('/payment/state...', end='')
    try:
        regPayNum = user['regPayNum']
    except KeyError:
        print('No regPayNum. Stop Method\n')
        return
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "regPayNum": f"{regPayNum}",
        "shopToken": f"{config.shopToken}"
    }
    # Рассчет подписи
    sign_str = payload['regPayNum'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign

    print("Check method /payment/state...", end='')
    request = s.post(url, data=json.dumps(payload), headers=json_headers).json()
    payment_state = request['state']
    if payment_state:
        print('OK')
        user['payment_state'] = payment_state
    else:
        print(f'Something wrong! url: {url} request: {request}')


def refund_payment():
    url = config.refund_rek_url
    # Сначала выполняем функцию создания платежа с указанием holdttl
    # будет новый regPayNum, он перезапишется в глобальный словарь user
    do_payment()
    # таймаут 3 секунды, иначе возвращается статус created
    time.sleep(3)
    print('/provision-services/refund...', end='')
    try:
        regPayNum = user['regPayNum']
    except KeyError:
        print('No regPayNum. Stop Method\n', end='')
        return
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "regPayNum": f"{regPayNum}",
        "orderId": f"{random.randint(10, 20)}",
        "shopToken": f"{config.shopToken}"
    }
    # Рассчет подписи
    sign_str = payload['regPayNum'] + '&' + payload['orderId'] + '&' + payload['shopToken'] + '&' + config.sec_key
    #print(f'userToken: {payload["userToken"]}\ncardToken: {payload["cardToken"]}\nshopToken: {payload["shopToken"]}')
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign
    #print('Check method /provision-services/refund...', end='')
    request = (s.post(url, data=json.dumps(payload), headers=json_headers)).json()
    result = request['resultState']
    if result == 'success':
        print('OK')
    else:
        print(f'Something wrong! url: {url} request: {request}')


def card_deactivation():
    url = config.card_deactivation_url
    print('/card/deatcivation...', end='')
    try:
        cardToken = user['cards'][0]['cardToken']  # Берем первую карту
    except IndexError:
        print('No cards. Stop method\n')
        return
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "userToken": f"{user['userToken']}",
        "shopToken": f"{config.shopToken}",
        "cardToken": f"{cardToken}"
    }

    # Рассчет подписи
    sign_str = payload['userToken'] + '&' + payload['cardToken'] + '&' + payload['shopToken'] + '&' + config.sec_key
    #print(f'userToken: {payload["userToken"]}\ncardToken: {payload["cardToken"]}\nshopToken: {payload["shopToken"]}')
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = sign
    #print('Check method /card/deatcivation...', end='')
    request = (s.post(url, data=json.dumps(payload), headers=json_headers)).json()
    result = request['resultState']
    if result == 'success':
        print('OK')
    else:
        print(f'Something wrong! url: {url} request: {request}')