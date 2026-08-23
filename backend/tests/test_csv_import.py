import io
import pytest

def test_csv_import_format1_hdfc_style(client, sample_user):
    csv_content = (
        "Date, Particulars, Withdrawal Amt., Deposit Amt.\n"
        "2026-08-20, UPI-SWIGGY-FOOD, 340.00, \n"
        "2026-08-21, Salary from TechCorp, , 75000.00\n"
    )

    response = client.post(
        "/api/v1/statements/import-csv",
        data={"user_id": sample_user.id},
        files={"file": ("hdfc_statement.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 2
    assert data["skipped_duplicates_count"] == 0
    assert data["total_parsed"] == 2

    txs = data["transactions"]
    swiggy_tx = next(t for t in txs if "SWIGGY" in t["description"])
    assert swiggy_tx["amount"] == 340.00
    assert swiggy_tx["type"] == "debit"
    assert swiggy_tx["merchant_name"] == "Swiggy"

    salary_tx = next(t for t in txs if "Salary" in t["description"])
    assert salary_tx["amount"] == 75000.00
    assert salary_tx["type"] == "credit"

def test_csv_import_format2_phonepe_style(client, sample_user):
    csv_content = (
        "Txn Date, Description, Amount, Type\n"
        "23/08/2026, Paid to Starbucks, 280.00, Debit\n"
        "22/08/2026, Cashback Received, 50.00, Credit\n"
    )

    response = client.post(
        "/api/v1/statements/import-csv",
        data={"user_id": sample_user.id},
        files={"file": ("phonepe_statement.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 2

    txs = data["transactions"]
    sb_tx = next(t for t in txs if "Starbucks" in t["description"])
    assert sb_tx["amount"] == 280.00
    assert sb_tx["merchant_name"] == "Starbucks"
    assert sb_tx["type"] == "debit"

def test_csv_import_format3_icici_style(client, sample_user):
    csv_content = (
        "Transaction Date, Narration, Debit, Credit\n"
        "21-Aug-2026, POS AMAZON RETAIL, 1299.00, \n"
        "22-Aug-2026, Zomato Order, 450.00, \n"
    )

    response = client.post(
        "/api/v1/statements/import-csv",
        data={"user_id": sample_user.id},
        files={"file": ("icici_statement.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 2

    txs = data["transactions"]
    amazon_tx = next(t for t in txs if "AMAZON" in t["description"])
    assert amazon_tx["amount"] == 1299.00
    assert amazon_tx["merchant_name"] == "Amazon"

def test_csv_import_deduplication(client, sample_user):
    csv_content = (
        "Date, Particulars, Withdrawal Amt., Deposit Amt.\n"
        "2026-08-20, UPI-BLINKIT-GROCERIES, 520.00, \n"
    )

    # First import
    resp1 = client.post(
        "/api/v1/statements/import-csv",
        data={"user_id": sample_user.id},
        files={"file": ("statement1.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    )
    assert resp1.status_code == 200
    assert resp1.json()["imported_count"] == 1
    assert resp1.json()["skipped_duplicates_count"] == 0

    # Duplicate re-import of same file
    resp2 = client.post(
        "/api/v1/statements/import-csv",
        data={"user_id": sample_user.id},
        files={"file": ("statement1_duplicate.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    )
    assert resp2.status_code == 200
    assert resp2.json()["imported_count"] == 0
    assert resp2.json()["skipped_duplicates_count"] == 1
