import requests
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
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


def init_driver():
    # Задаем параметры
    cd_path = 'src/chromedriver'
    options = Options()
    options.add_argument('--headless')  # скрывать окна хрома
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(cd_path, options=options)
    driver.implicitly_wait(30)  # неявное ожидание драйвера
    return driver


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
    payurl = request['payUrl']
    methodType = request['methodType']
    #print(f'sign: {sign}\nshopToken: {shopToken}\nregPayNum: {regPayNum}\npayurl: {payurl}\nmethodType: {methodType}')
    if sign != '' and methodType == 'GET' and shopToken != '' and 'https://demo-acq.bisys.ru/cardpay/card?order=' in payurl and regPayNum != '':
        print('OK')
    else:
        print(f'Something wrong!\nrequest_status_code: {r.status_code}\nrequest: {request}')

    return payurl


def payment_of_the_created_anonymous_pay():
    payUrl = create_anonimus_pay()
    driver = init_driver()
    wait = WebDriverWait(driver, 3)  # Задал переменную, чтоб настроить явное ожидание элемента (сек)

    print('check payment_of_the_created_anonymous_pay...', end='')
    driver.get(payUrl)
    # Ввожу номер карты в 4 подхода, т.к. если вводить слишком быстро, то форма ломается
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#pan'))).send_keys('4000')
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#pan'))).send_keys('0000')
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#pan'))).send_keys('0000')
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#pan'))).send_keys('0002')
    # Тоже в 2 подхода, чтоб не сломать форму
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#exp'))).send_keys('01')
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#exp'))).send_keys('21')

    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="holder"]'))).send_keys(f'{config.card_owner}')
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="secret"]'))).send_keys(f'{config.cvv}')

    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="buttonpay"]'))).click()
    # парсим текст результата оплаты
    payment_result = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div[1]/div[2]/span'))).get_attribute('innerHTML')

    if payment_result == 'Ваш платеж произведен успешно':
        print('OK')
    else:
        print(f'Something wrong! payment_result: {payment_result}')

    driver.quit()


def get_cards_rek():
    headers = {'Content-Type': 'application/json'}
    url = config.get_cards_rek_url
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "userToken": "0356c2b6-70c1-41da-8e10-334712ad4560",
        "shopToken": "1a4c0d33-010c-4365-9c65-4c7f9bb415d5"
    }
    r = s.post(url, data=json.dumps(payload), headers=headers)
    print('Check method "get/cards"...', end='')
    request = r.json()
    cards = request['cards']
    if cards != '':
        print('OK')
    else:
        print(f'Somesing wrong! request: {request}')
    return cards


def card_registration_rek():
    headers = {'Content-Type': 'application/json'}
    url = config.card_registration_url
    payload = {
        "sign": "C5A5386EBADC3D0574CCB7A81820698A",
        "userToken": "0356c2b6-70c1-41da-8e10-334712ad4560",
        "shopToken": "1a4c0d33-010c-4365-9c65-4c7f9bb415d5"
    }
    # Сначала чекаем, нет ли в уже зарегистрированных картах той, которую мы собираемся зарегать
    cards = get_cards_rek()
    # Чекаем есть ли привязанные карты
    if cards:
        print('Card alredy registred. Start deactivation...')
        cardToken = cards[0]['cardToken']
        # Зацикленная функция. Будет исполнять сама себя, пока не кончатся привязанные карты
        card_deactivation_rek(cardToken)
        card_registration_rek()
        # Когда привязанные карты кончились, начинаем регистрацию
    else:
        print('Check method "card/registration"...', end='')
        r = s.post(url, data=json.dumps(payload), headers=headers)
        request = r.json()
        registration_url = request['payUrl']
        if registration_url:
            driver = init_driver()
            driver.get(registration_url)
            wait = WebDriverWait(driver, 3)  # Явное ожидание элемента (сек)
            # Ввожу номер карты в 4 подхода, т.к. если вводить слишком быстро, то форма ломается
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#pan'))).send_keys('4000')
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#pan'))).send_keys('0000')
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#pan'))).send_keys('0000')
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#pan'))).send_keys('0002')
            # Тоже в 2 подхода, чтоб не сломать форму
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#exp'))).send_keys('01')
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#exp'))).send_keys('21')

            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="holder"]'))).send_keys(f'{config.card_owner}')
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="secret"]'))).send_keys(f'{config.cvv}')
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="buttonpay"]'))).click()
            registration_result = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div/div/span'))).get_attribute(
                'innerHTML')
            if registration_result == 'Ваша карта успешно зарегистрирована':
                print('OK')
            else:
                print(f'Something wrong! registration_result: {registration_result}')
            driver.quit()

            # После успешной регистрации вытаскиваем cardToken и запускаем функцию отвязки карты
            cards = get_cards_rek()
            cardToken = cards[0]['cardToken']
            card_deactivation_rek(cardToken)

        else:
            print(f"Can't get registration_url. Request: {request}")


def card_deactivation_rek(cardToken):
    headers = {'Content-Type': 'application/json'}
    url = config.card_deactivation_url
    payload = {
        "sign": "200CB466B41AD3C9FA1A546CC7BB86E2",
        "userToken": "0356c2b6-70c1-41da-8e10-334712ad4560",
        "cardToken": f"{cardToken}",
        "shopToken": "1a4c0d33-010c-4365-9c65-4c7f9bb415d5"
    }
    sign_str = payload['userToken'] + '&' + payload['cardToken'] + '&' + payload['shopToken'] + '&' + config.sec_key
    pre_sign = (hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()).upper()
    sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
    payload['sign'] = f'{sign}'
    print('Check method "card/deactivation"...', end='')
    r = s.post(url, data=json.dumps(payload), headers=headers)
    request = r.json()
    resultState = request['resultState']
    if resultState == 'success':
        print('OK')
    else:
        print(f'Something wrong! Request: {request}')


if __name__ == '__main__':
    try:
        payment_of_the_created_anonymous_pay()
        card_registration_rek()
    except KeyboardInterrupt:
        print('Program has been stop manually')
