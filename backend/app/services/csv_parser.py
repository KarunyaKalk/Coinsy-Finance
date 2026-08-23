import io
import re
from datetime import datetime, date
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd

DATE_COL_CANDIDATES = ["date", "txn date", "transaction date", "value date", "time", "trans date"]
DESC_COL_CANDIDATES = ["description", "particulars", "narration", "remarks", "details", "payee", "transaction remarks", "note"]
DEBIT_COL_CANDIDATES = ["debit", "withdrawal", "withdrawal amt.", "withdrawal amount", "dr", "dr amount", "spent"]
CREDIT_COL_CANDIDATES = ["credit", "deposit", "deposit amt.", "deposit amount", "cr", "cr amount", "received"]
AMOUNT_COL_CANDIDATES = ["amount", "txn amount", "transaction amount", "amt"]
TYPE_COL_CANDIDATES = ["type", "txn type", "transaction type", "cr/dr", "dr/cr", "debit/credit", "direction"]

def parse_flexible_date(val: Any) -> Optional[date]:
    if pd.isna(val) or not str(val).strip():
        return None
    val_str = str(val).strip()
    
    # Common format patterns
    date_formats = [
        "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y",
        "%d %b %Y", "%d-%b-%Y", "%d %B %Y", "%d-%B-%Y",
        "%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d"
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(val_str, fmt).date()
        except ValueError:
            continue
            
    # Fallback using pandas date parser
    try:
        parsed = pd.to_datetime(val_str, dayfirst=True)
        return parsed.date()
    except Exception:
        return None

def extract_merchant_and_mode(description: str) -> Tuple[Optional[str], str]:
    if not description:
        return None, "UPI"
        
    desc_upper = description.upper()
    
    # Detect payment mode
    payment_mode = "UPI"
    if "POS" in desc_upper or "CARD" in desc_upper:
        payment_mode = "Card"
    elif any(k in desc_upper for k in ["NEFT", "IMPS", "RTGS", "NETBANKING"]):
        payment_mode = "NetBanking"
    elif "CASH" in desc_upper:
        payment_mode = "Cash"

    # Extract merchant name
    merchant = None
    # Pattern: UPI/MerchantName/... or UPI-MerchantName-...
    upi_match = re.search(r'UPI[/-]([A-Za-z0-9\s&._]+)[/-]', description, re.IGNORECASE)
    if upi_match:
        merchant = upi_match.group(1).strip()
    else:
        # Pattern: Swiggy, Zomato, Amazon, Uber, Blinkit, etc.
        known_merchants = [
            "Swiggy", "Zomato", "Amazon", "Flipkart", "Uber", "Ola", "Blinkit",
            "Zepto", "Myntra", "BookMyShow", "MakeMyTrip", "Paytm", "PhonePe",
            "Starbucks", "McDonalds", "Dominos", "Dunzo", "Reliance", "Tata"
        ]
        for km in known_merchants:
            if km.lower() in description.lower():
                merchant = km
                break
                
    if not merchant and len(description.split()) <= 3:
        merchant = description.strip()

    if merchant:
        merchant = merchant.strip().title()

    return merchant, payment_mode

def parse_csv_statement(content_bytes: bytes) -> List[Dict[str, Any]]:
    # Try different encodings
    for encoding in ["utf-8", "latin1", "cp1252"]:
        try:
            df = pd.read_csv(io.BytesIO(content_bytes), encoding=encoding)
            break
        except Exception:
            continue
    else:
        raise ValueError("Could not parse CSV file. Unsupported format or encoding.")

    # Clean column headers
    df.columns = [str(c).strip() for c in df.columns]
    cols_lower = {c: str(c).strip().lower() for c in df.columns}
    
    # Identify Date column
    date_col = None
    for orig_col, lower_col in cols_lower.items():
        if any(cand == lower_col for cand in DATE_COL_CANDIDATES):
            date_col = orig_col
            break
            
    # Identify Description column
    desc_col = None
    for orig_col, lower_col in cols_lower.items():
        if any(cand == lower_col for cand in DESC_COL_CANDIDATES):
            desc_col = orig_col
            break
            
    # Identify Amount columns (Debit/Credit vs Single Amount)
    debit_col = None
    credit_col = None
    amount_col = None
    type_col = None
    
    for orig_col, lower_col in cols_lower.items():
        if any(cand == lower_col for cand in DEBIT_COL_CANDIDATES):
            debit_col = orig_col
        elif any(cand == lower_col for cand in CREDIT_COL_CANDIDATES):
            credit_col = orig_col
        elif any(cand == lower_col for cand in AMOUNT_COL_CANDIDATES):
            amount_col = orig_col
        elif any(cand == lower_col for cand in TYPE_COL_CANDIDATES):
            type_col = orig_col

    if not date_col:
        raise ValueError("Could not identify Date column in CSV.")
    if not desc_col:
        raise ValueError("Could not identify Description column in CSV.")

    parsed_transactions = []
    
    for idx, row in df.iterrows():
        txn_date = parse_flexible_date(row[date_col])
        if not txn_date:
            continue  # Skip header/footer noise rows
            
        desc = str(row[desc_col]).strip() if pd.notna(row[desc_col]) else "Unspecified"
        
        amt = 0.0
        txn_type = "debit"
        
        # Scenario A: Separate Debit and Credit columns
        if debit_col or credit_col:
            raw_debit = str(row[debit_col]).replace(",", "").strip() if debit_col and pd.notna(row[debit_col]) else ""
            raw_credit = str(row[credit_col]).replace(",", "").strip() if credit_col and pd.notna(row[credit_col]) else ""
            
            try:
                debit_val = float(raw_debit) if raw_debit and raw_debit != "-" else 0.0
            except ValueError:
                debit_val = 0.0
                
            try:
                credit_val = float(raw_credit) if raw_credit and raw_credit != "-" else 0.0
            except ValueError:
                credit_val = 0.0
                
            if debit_val > 0:
                amt = debit_val
                txn_type = "debit"
            elif credit_val > 0:
                amt = credit_val
                txn_type = "credit"
            else:
                continue  # 0 amount row
                
        # Scenario B: Single Amount column + Optional Type column
        elif amount_col:
            raw_amt_str = str(row[amount_col]).replace(",", "").strip() if pd.notna(row[amount_col]) else ""
            try:
                raw_amt = float(raw_amt_str)
            except ValueError:
                continue
                
            if raw_amt < 0:
                amt = abs(raw_amt)
                txn_type = "debit"
            else:
                amt = raw_amt
                txn_type = "debit"
                if type_col and pd.notna(row[type_col]):
                    type_str = str(row[type_col]).strip().lower()
                    if any(c in type_str for c in ["cr", "credit", "+", "deposit"]):
                        txn_type = "credit"
                    elif any(c in type_str for c in ["dr", "debit", "-", "withdrawal"]):
                        txn_type = "debit"

        merchant, payment_mode = extract_merchant_and_mode(desc)
        
        parsed_transactions.append({
            "date": txn_date,
            "amount": round(amt, 2),
            "type": txn_type,
            "description": desc,
            "raw_text": f"CSV_ROW: {row.to_dict()}",
            "merchant_name": merchant,
            "payment_mode": payment_mode
        })
        
    return parsed_transactions
