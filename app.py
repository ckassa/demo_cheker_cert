import time
from . import anonimus_pay
from . import rekurent_pay
from . import fiscal_cash_pay
import config
from src.manager import do_alarm
from loguru import logger

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


@logger.catch()
def main():
    try:
        # Сначала сбросим все что есть в выходных данных (чтоб не было дублей)
        anonimus_pay.output.clear()
        rekurent_pay.rekurrent_pay_output.clear()
        fiscal_cash_pay.output.clear()
        # Блок с анонимами
        anonimus_pay.payment_created_pay()
        # Блок с рекуррентами
        #print('\nCheck rekurrent methods:\n')
        rekurent_pay.rekurrent_pay_output.append('\nCheck rekurrent methods:\n\n')
        rekurent_pay.user_registration()
        rekurent_pay.get_user_status()
        rekurent_pay.card_registration()
        # Если не взять паузу, то autopays не успевает записать привязанную карту и возвращает пустой массив с картами
        time.sleep(3)
        rekurent_pay.get_cards_rek()
        rekurent_pay.do_payment()
        time.sleep(3)
        rekurent_pay.get_pay_state()
        rekurent_pay.confirm_pay()
        rekurent_pay.refund_payment()
        rekurent_pay.card_deactivation()
        #print('\nCheck fiscalCash methods:\n')
        fiscal_cash_pay.output.append('\nCheck fiscalCash methods:\n\n')
        # Блок с фискализацией наличных
        fiscal_cash_pay.create_anonimus_pay()
        fiscal_cash_pay.check_pay_status()
        fiscal_cash_pay.get_fiscal_check()
        output = ''.join(anonimus_pay.output + rekurent_pay.rekurrent_pay_output + fiscal_cash_pay.output)
        return output

    except KeyboardInterrupt:
        print('Program stopped')
    except Exception as e:
        t_alarmtext = f'tg_mon_bot (app.py): {str(e)}'
        do_alarm(t_alarmtext)
        logger.error(f'Other except error Exception', exc_info=True)