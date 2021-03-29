import time
import anonimus_pay
import rekurent_pay
import fiscal_cash_pay
from loguru import logger

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


def autotest_anonimus_pay():
    anonimus_pay.create_anonimus_pay()
    anonimus_pay.payment_created_pay()
    anonimus_pay.check_pay_status()


def autotest_rekurrent_pay():
    rekurent_pay.user_registration()
    rekurent_pay.get_user_status()
    rekurent_pay.card_registration()
    # Если не взять паузу, то autopays может не успеть записать привязанную карту и возвращает пустой массив с картами
    time.sleep(3)
    rekurent_pay.get_cards_rek()
    rekurent_pay.do_payment()
    time.sleep(3)
    rekurent_pay.get_pay_state()
    rekurent_pay.confirm_pay()
    rekurent_pay.refund_payment()
    rekurent_pay.card_deactivation()


def autotest_fiscal_cash_pay():
    fiscal_cash_pay.create_anonimus_pay()
    fiscal_cash_pay.check_pay_status()
    fiscal_cash_pay.get_fiscal_check()


if __name__ == '__main__':
    try:
        autotest_anonimus_pay()
        autotest_rekurrent_pay()
        autotest_fiscal_cash_pay()
    except KeyboardInterrupt:
        logger.info('Program has been stoped manually')