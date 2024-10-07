import uuid
import random
from datetime import datetime, timezone

from faker import Faker
faker = Faker()

TXN_TYPES = ['ach','debit','credit', 'transfer', 'cash', 'refund', 'interest', 'adjustment', 'payment']
STATUSES = ['complete','incomplete','pending', 'blocked', 'archived', 'initial']
CURRENCIES = ['usd','yen', 'eur']


def construct(department_id):
    return {
            "req_id": f"{uuid.UUID(int=random.getrandbits(128), version=4)}",
            "id": f"{uuid.UUID(int=random.getrandbits(128), version=4)}",
            "type": "transaction",
            "department_id": department_id,
            "subtype": random.choice(TXN_TYPES),
            "occurred_at": f"{faker.date_time_between_dates(datetime_start=datetime(2020,1,1), datetime_end=datetime(2024,12,31))}",
            "status": random.choice(STATUSES),
            "sent_amount": faker.pyint(min_value=10, max_value=100000),
            "sent_currency": random.choice(CURRENCIES),
            "sender_id": f"{uuid.UUID(int=random.getrandbits(128), version=4)}",
            "sender_ip_address": f"{faker.ipv4()}",
            "received_amount": faker.pyint(min_value=10, max_value=100000),
            "received_currency": random.choice(CURRENCIES),
            "receiver_id": f"{uuid.UUID(int=random.getrandbits(128), version=4)}",
            "receiver_ip_address": f"{faker.ipv4()}",
            "amount": faker.pyint(min_value=10, max_value=100000),
            "exchange_rate": 1.11,
            "metadata": {
                "request_received_from_client": f"{datetime.now(timezone.utc)}",
                "risk_score": faker.pyint(min_value=10, max_value=100),
                "is_blocked": faker.pybool(),
            },
    }
