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

s = requests.Session()
sert_path = 'src' + os.sep + 'cert.pem'
key_path = 'src' + os.sep + 'dec.key'
s.cert = (sert_path, key_path)  # Приватный ключ через тектсовик я вытащил из серта p12, затем командой "openssl rsa -in my.key_encrypted -out my.key_decrypted" (со вводом пароля) расшифровал закрытый ключ


def create_anonimus_pay():
    print('Check method create anonimus pay...', end='')
    url = config.url
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
    # print(f'sign: {sign}\nshopToken: {shopToken}\nregPayNum: {regPayNum}\npayurl: {payurl}\nmethodType: {methodType}')
    if sign != '' and methodType == 'GET' and shopToken != '' and 'https://demo-acq.bisys.ru/cardpay/card?order=' in payurl and regPayNum != '':
        print('OK')
    else:
        print(f'Something wrong!\nrequest_status_code: {r.status_code}\nrequest: {request}')

    return payurl


def payment_of_the_created_anonymous_payment():
    payUrl = create_anonimus_pay()
    cd_dir_path = 'src' + os.sep + 'chromedriver'
    chrome_options = Options()  # задаем параметры запуска драйвера, чтоб не крашился (когда работает во много потоков)
    #chrome_options.add_argument('--headless')  # скрывать окна хрома
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    #chrome_options.add_argument("--window-size=1980,1024")
    driver = webdriver.Chrome(cd_dir_path, chrome_options=chrome_options)
    driver.implicitly_wait(30)  # неявное ожидание драйвера
    wait = WebDriverWait(driver, 3)  # Задал переменную, чтоб настроить явное ожидание элемента (сек)

    driver.get(payUrl)

    pan = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#pan')))
    pan.send_keys(f'{config.pan}')

    exp = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="exp"]')))
    exp.send_keys(f'{config.exp}')

    card_owner = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="holder"]')))
    card_owner.send_keys(f'{config.card_owner}')

    cvv = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="secret"]')))
    cvv.send_keys(f'{config.cvv}')

    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="buttonpay"]'))).click()

    time.sleep(20)
    #driver.close()


payment_of_the_created_anonymous_payment()