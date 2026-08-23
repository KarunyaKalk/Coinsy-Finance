import io
from datetime import date
from app.services.pdf_parser.masking import mask_account_numbers
from app.services.pdf_parser.base import PasswordProtectedPDFError
from app.services.pdf_parser.generic_table_parser import GenericTablePDFParser
from app.services.pdf_parser.llm_pdf_parser import LLMAssistedPDFParser, fallback_text_regex_parser
from app.services.pdf_parser.manager import PDFStatementManager

def test_account_number_masking():
    # 14-digit bank account number
    raw_desc = "Transfer to A/C 50100123456789 Swiggy"
    masked = mask_account_numbers(raw_desc)
    assert "50100123456789" not in masked
    assert "XXXXXXXXXX6789" in masked

    # 16-digit credit card number
    raw_card = "Payment for Card 4111222233334444 Amazon"
    masked_card = mask_account_numbers(raw_card)
    assert "4111222233334444" not in masked_card
    assert "XXXX-XXXX-XXXX-4444" in masked_card

def test_llm_pdf_fallback_text_regex_parser():
    text = (
        "HDFC BANK STATEMENT\n"
        "20/08/2026 UPI/SWIGGY/A/C 50100123456789 340.00 Dr\n"
        "21/08/2026 Salary Credit 75000.00 Cr\n"
    )
    txs = fallback_text_regex_parser(text)
    assert len(txs) == 2
    assert txs[0]["amount"] == 340.00
    assert txs[0]["type"] == "debit"
    assert txs[1]["amount"] == 75000.00
    assert txs[1]["type"] == "credit"

def test_pdf_manager_masking_integration(monkeypatch):
    # Mock LLMAssistedPDFParser to return transactions with full account numbers
    unmasked_txs = [
        {
            "date": date(2026, 8, 23),
            "amount": 1500.00,
            "type": "debit",
            "description": "UPI to A/C 98765432109876 for Rent",
            "merchant_name": "Landlord A/C 98765432109876",
            "raw_text": "RAW_ROW 98765432109876",
            "payment_mode": "UPI"
        }
    ]

    manager = PDFStatementManager()
    monkeypatch.setattr(
        manager.parsers[0],
        "parse",
        lambda pdf_bytes, password=None: []
    )
    monkeypatch.setattr(
        manager.parsers[1],
        "parse",
        lambda pdf_bytes, password=None: unmasked_txs
    )

    results = manager.parse_pdf_statement(b"fake_pdf_content")
    assert len(results) == 1
    assert "98765432109876" not in results[0]["description"]
    assert "XXXXXXXXXX9876" in results[0]["description"]
    assert "98765432109876" not in results[0]["merchant_name"]

def test_password_protected_pdf_exception_handling(client, sample_user, monkeypatch):
    def mock_parse_password_error(pdf_bytes, password=None):
        if password != "correct_secret":
            raise PasswordProtectedPDFError("PDF is password-protected or password supplied is incorrect.")
        return [
            {
                "date": date(2026, 8, 23),
                "amount": 200.0,
                "type": "debit",
                "description": "Protected Statement Txn",
                "merchant_name": "ProtectedMerchant",
                "payment_mode": "UPI"
            }
        ]

    from app.api.statements import pdf_statement_manager
    monkeypatch.setattr(pdf_statement_manager, "parse_pdf_statement", mock_parse_password_error)

    # Attempt 1: Without password -> 400 Bad Request with password required error
    resp1 = client.post(
        "/api/v1/statements/import-pdf",
        data={"user_id": sample_user.id},
        files={"file": ("protected.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")}
    )
    assert resp1.status_code == 400
    assert "password-protected" in resp1.json()["detail"].lower()

    # Attempt 2: With correct password -> Success 200
    resp2 = client.post(
        "/api/v1/statements/import-pdf",
        data={"user_id": sample_user.id, "password": "correct_secret"},
        files={"file": ("protected.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")}
    )
    assert resp2.status_code == 200
    assert resp2.json()["imported_count"] == 1
    assert resp2.json()["transactions"][0]["description"] == "Protected Statement Txn"
