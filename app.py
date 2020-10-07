import time
import anonimus_pay
import rekurent_pay
import fiscal_cash_pay
from src import config
from loguru import logger

logger.add('src/debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


@logger.catch  # Логировать исключения из функции
def main():
    ## Блок с анонимами
    #anonimus_pay.payment_created_pay()
    # Блок с рекуррентами
    print('\nCheck rekurrent methods:\n')
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
    rekurent_pay.do_payment_rezerv()
    rekurent_pay.update_pers_acc()
    rekurent_pay.card_deactivation()
    print('\nCheck fiscalCash methods:\n')
    ## Блок с фискализацией наличных
    #fiscal_cash_pay.create_anonimus_pay()
    #fiscal_cash_pay.check_pay_status()
    #fiscal_cash_pay.get_fiscal_check()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Program stopped')
    #except Exception as e:
    #    t_alarmtext = f'tg_mon_bot (app.py): {str(e)}'
    #    do_alarm(t_alarmtext)
    #    logger.error(f'Other except error Exception', exc_info=True)