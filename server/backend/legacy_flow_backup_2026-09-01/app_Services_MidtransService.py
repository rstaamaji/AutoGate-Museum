import midtransclient

from app.config import settings


def create_payment(
    order_id: str,
    amount: int,
    ticket_code: str,
    expiry_hours: int,
) -> dict:
    snap = midtransclient.Snap(
        is_production=settings.MIDTRANS_IS_PRODUCTION,
        server_key=settings.MIDTRANS_SERVER_KEY,
    )

    parameter = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": amount,
        },
        "item_details": [
            {
                "id": ticket_code,
                "price": amount,
                "quantity": 1,
                "name": "Karcis Parkir Museum",
            }
        ],
        "expiry": {
            "unit": "hours",
            "duration": expiry_hours,
        },
    }

    return snap.create_transaction(parameter)