
"""\
Demo: handle incoming SMS messages by replying to them

Simple demo app that listens for incoming SMS messages, displays the sender's number
and the messages, then replies to the SMS by saying "thank you"
"""

import logging
import time

from config import UserConfig

PORT = '/dev/ttyGSM1'
BAUDRATE = 115200
PIN = None # SIM card PIN (if any)

from gsmmodem.modem import GsmModem

def handle_sms(sms):
    logging.debug(u'== SMS message received ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}\n'.format(sms.number, sms.time, sms.text))
    if sms.number == UserConfig.authorizedNumber:
        if UserConfig.SMSControl:
            if sms.text.lower() == 'set mode realtime':
                # set mode
                UserConfig.mode = 'realtime'
                logging.debug('Mode has been set to realtime by SMS')
                sms.reply(u'Mode has been set to realtime')

            elif sms.text.lower() == 'set mode batch':
                # set mode
                UserConfig.mode = 'batch'
                logging.debug('Mode has been set to batch by SMS')
                sms.reply(u'Mode has been set to batch')

            elif sms.text.lower() == 'set mode interval':
                # set mode
                UserConfig.mode = 'interval'
                logging.debug('Mode has been set to interval by SMS')
                sms.reply(u'Mode has been set to interval')

            elif sms.text.lower() == 'set mode ondemand':
                # set mode
                UserConfig.mode = 'ondemand'
                logging.debug('Mode has been set to ondemand by SMS')
                sms.reply(u'Mode has been set to ondemand')

            elif sms.text.lower() == 'q mode':
                # query mode
                logging.debug('Mode has been queried by SMS')
                sms.reply(u'Mode is')

            elif sms.text.lower() == 'battery':
                # query mode
                logging.debug('Status of charging has been queried')
                sms.reply(u'Charging 12V.3')

            elif sms.text.lower() == 'takephoto':
                # query mode
                logging.debug('Photo has been requested')
                sms.reply(u'Photo taken')

        else:
            logging.debug('SMS Control not allowed')
    else:
        logging.debug('Number is not authorized')


def main():
    print('Initializing modem...')
    # Uncomment the following line to see what the modem is doing:
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    modem = GsmModem(PORT, BAUDRATE, smsReceivedCallbackFunc=handle_sms, AT_CNMI="2,1,0,1")
    modem.smsTextMode = False
    modem.connect(PIN)
    print('Waiting for SMS message...')
    try:
        time.sleep(100)
        #modem.rxThread.join(2**31) # Specify a (huge) timeout so that it essentially blocks indefinitely, but still receives CTRL+C interrupt signal
    finally:
        modem.close()

if __name__ == '__main__':
    main()
