import os
import logging
from random import randint

logger = logging.getLogger(__name__)


def generate_code(length=6):
    return str(randint(10**(length-1), 10**length - 1))


def send_sms(telephone, message):
    """Send an SMS using Twilio if configured; otherwise log the message for dev."""
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_FROM_NUMBER')

    if account_sid and auth_token and from_number:
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            client.messages.create(body=message, from_=from_number, to=telephone)
            return True
        except Exception as exc:
            logger.exception('Failed to send SMS via Twilio: %s', exc)
            return False
    else:
        # Development fallback — log the message so developer can see the code
        logger.info('SMS to %s: %s', telephone, message)
        return True
