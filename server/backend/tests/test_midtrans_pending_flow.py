import unittest
from datetime import datetime, timedelta, timezone

from app.Http.Controllers.PaymentController import (
    is_pending_ticket_expired,
    validate_exit_ticket,
)
from app.Models.ParkingTicket import ParkingTicket


class DummyDB:
    def __init__(self, ticket):
        self.ticket = ticket

    def query(self, model):
        return DummyQuery(self.ticket)


class DummyQuery:
    def __init__(self, ticket):
        self.ticket = ticket

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.ticket


class MidtransPendingFlowTests(unittest.TestCase):
    def test_pending_ticket_is_expired_after_12_hours(self):
        ticket = ParkingTicket(
            ticket_code="TKT-1",
            barcode_token="abc",
            plate_number="B1234XYZ",
            status="pending",
            created_at=datetime.now(timezone.utc) - timedelta(hours=13),
        )

        self.assertTrue(is_pending_ticket_expired(ticket))

    def test_validate_exit_rejects_pending_ticket(self):
        ticket = ParkingTicket(
            ticket_code="TKT-1",
            barcode_token="abc",
            plate_number="B1234XYZ",
            status="pending",
            created_at=datetime.now(timezone.utc),
        )

        result = validate_exit_ticket(DummyDB(ticket), "abc")
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "pending")

    def test_validate_exit_allows_paid_ticket_once(self):
        ticket = ParkingTicket(
            ticket_code="TKT-2",
            barcode_token="paid-token",
            plate_number="B9999XYZ",
            status="paid",
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )

        result = validate_exit_ticket(DummyDB(ticket), "paid-token")
        self.assertTrue(result["valid"])
        self.assertEqual(result["status"], "paid")


if __name__ == "__main__":
    unittest.main()
