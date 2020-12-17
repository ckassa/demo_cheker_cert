import time
from . import anonimus_pay
from . import rekurent_pay
from . import fiscal_cash_pay
from src.manager import do_alarm
from loguru import logger

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


def autotest_anonimus_pay():
    # Сначала сбросим все что есть в выходных данных (чтоб не было дублей)
    anonimus_pay.output.clear()
    anonimus_pay.create_anonimus_pay()
    anonimus_pay.payment_created_pay()
    anonimus_pay.check_pay_status()
    return anonimus_pay.output


def autotest_rekurrent_pay():
    rekurent_pay.output.clear()
    rekurent_pay.user_registration()
    rekurent_pay.get_user_status()
    rekurent_pay.card_registration()
    ## Если не взять паузу, то autopays не успевает записать привязанную карту и возвращает пустой массив с картами
    time.sleep(3)
    rekurent_pay.get_cards_rek()
    rekurent_pay.do_payment()
    time.sleep(3)
    rekurent_pay.get_pay_state()
    rekurent_pay.confirm_pay()
    rekurent_pay.refund_payment()
    rekurent_pay.card_deactivation()
    return rekurent_pay.output


def autotest_fiscal_cash_pay():
    fiscal_cash_pay.create_anonimus_pay()
    fiscal_cash_pay.check_pay_status()
    fiscal_cash_pay.get_fiscal_check()
    return fiscal_cash_pay.output


def main():
    #try:
    return ''.join(autotest_anonimus_pay() + autotest_rekurrent_pay() + autotest_fiscal_cash_pay())
    #except KeyboardInterrupt:
    #    print('Program stopped')
    ##except Exception as e:
    ##    t_alarmtext = f'demo_checker (app.py): {str(e)}'
    ##    do_alarm(t_alarmtext)
    ##    logger.error(f'Other except error Exception', exc_info=True)

#@logger.catch()
#def main():
#    try:
#        #fiscal_cash_pay.output.append('\nCheck fiscalCash methods:\n\n')
#        ## Блок с фискализацией наличных
#        #fiscal_cash_pay.create_anonimus_pay()
#        #fiscal_cash_pay.check_pay_status()
#        #fiscal_cash_pay.get_fiscal_check()
#        #output = ''.join(anonimus_pay.output + rekurent_pay.rekurrent_pay_output + fiscal_cash_pay.output)
#        #return output
#
#    except KeyboardInterrupt:
#        print('Program stopped')
#    #except Exception as e:
#    #    t_alarmtext = f'demo_checker (app.py): {str(e)}'
#    #    do_alarm(t_alarmtext)
#    #    logger.error(f'Other except error Exception', exc_info=True)