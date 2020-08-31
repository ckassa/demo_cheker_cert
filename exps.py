import hashlib
from src import config

payload = {
    "sign": "200CB466B41AD3C9FA1A546CC7BB86E2",
    "userToken": "0356c2b6-70c1-41da-8e10-334712ad4560",
    "cardToken": "0356c2b6-70c1-41da-8e10-334712ad3450",
    "shopToken": "1a4c0d33-010c-4365-9c65-4c7f9bb415d5"
}
sign_str = (payload['userToken'] + '&' + payload['cardToken'] + '&' + payload['shopToken'] + '&' + config.sec_key).upper()
pre_sign = hashlib.md5(f"{sign_str}".encode('utf-8')).hexdigest()
sign = (hashlib.md5(f"{pre_sign}".encode('utf-8')).hexdigest()).upper()
print(sign)