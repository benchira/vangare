import os

import requests
from django.conf import settings


PAYMEE_BASE_URL = os.getenv('PAYMEE_BASE_URL', 'https://paymee.tn/api')
PAYMEE_API_KEY = os.getenv('PAYMEE_API_KEY', '')
PAYMEE_API_SECRET = os.getenv('PAYMEE_API_SECRET', '')

KONNECT_BASE_URL = os.getenv('KONNECT_BASE_URL', 'https://api.konnect.tn')
KONNECT_API_KEY = os.getenv('KONNECT_API_KEY', '')
KONNECT_RECEIVER_ID = getattr(settings, 'KONNECT_RECEIVER_ID', os.getenv('KONNECT_RECEIVER_ID', ''))


def build_payment_payload(amount_tnd, order_id, description, return_url):
    return {
        'amount': float(amount_tnd),
        'order_id': order_id,
        'description': description,
        'return_url': return_url,
    }


def create_paymee_payment(amount_tnd, order_id, description, return_url):
    if not PAYMEE_API_KEY or not PAYMEE_API_SECRET:
        raise ValueError('Paymee API keys are not configured')

    payload = build_payment_payload(amount_tnd, order_id, description, return_url)
    headers = {
        'Authorization': f'Bearer {PAYMEE_API_KEY}',
        'Content-Type': 'application/json',
    }
    response = requests.post(f'{PAYMEE_BASE_URL}/payments', json=payload, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()


def create_konnect_payment(amount_tnd, order_id, description, return_url):
    if not KONNECT_API_KEY:
        raise ValueError('Konnect API key is not configured')
    payload = build_payment_payload(amount_tnd, order_id, description, return_url)
    # include receiver id when configured
    if KONNECT_RECEIVER_ID:
        payload['receiver_id'] = KONNECT_RECEIVER_ID
    headers = {
        'Authorization': f'Bearer {KONNECT_API_KEY}',
        'Content-Type': 'application/json',
    }
    response = requests.post(f'{KONNECT_BASE_URL}/payments', json=payload, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()
