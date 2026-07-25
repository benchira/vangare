import os
import requests

ARAMEX_BASE_URL = os.getenv('ARAMEX_BASE_URL', 'https://api.aramex.com')
ARAMEX_API_KEY = os.getenv('ARAMEX_API_KEY', '')


def create_aramex_shipment(order_reference, recipient_address, recipient_phone):
    if not ARAMEX_API_KEY:
        raise ValueError('Aramex API key is not configured')

    payload = {
        'order_reference': order_reference,
        'recipient_address': recipient_address,
        'recipient_phone': recipient_phone,
        'service': 'cash_on_delivery',
    }
    response = requests.post(f'{ARAMEX_BASE_URL}/shipments', json=payload, headers={'Authorization': f'Bearer {ARAMEX_API_KEY}'}, timeout=20)
    response.raise_for_status()
    return response.json()
