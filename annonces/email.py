import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_verification_email(email, code):
    subject = 'Votre code de vérification'
    message = f"Votre code de vérification est : {code}\n\nSi vous n'avez pas demandé ce code, ignorez cet e-mail."
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)

    try:
        if from_email:
            send_mail(subject, message, from_email, [email], fail_silently=False)
            return True
        else:
            logger.info('Email to %s: %s', email, message)
            return True
    except Exception as exc:
        logger.exception('Failed to send verification email to %s: %s', email, exc)
        return False
