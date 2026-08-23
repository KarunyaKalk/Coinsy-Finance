import io
from typing import List, Dict, Any, Optional
import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect
from app.services.pdf_parser.base import BaseBankPDFParser, PasswordProtectedPDFError
from app.services.csv_parser import parse_flexible_date, extract_merchant_and_mode, DATE_COL_CANDIDATES, DESC_COL_CANDIDATES, DEBIT_COL_CANDIDATES, CREDIT_COL_CANDIDATES, AMOUNT_COL_CANDIDATES

class GenericTablePDFParser(BaseBankPDFParser):
    def parse(self, pdf_bytes: bytes, password: Optional[str] = None) -> List[Dict[str, Any]]:
        transactions = []
        
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes), password=password) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                            
                        # Find header row
                        header_idx = None
                        cols_lower = {}
                        for idx, row in enumerate(table):
                            if not row:
                                continue
                            row_str = [str(cell).strip().lower() for cell in row if cell]
                            if any(any(c in cell for c in DATE_COL_CANDIDATES) for cell in row_str) and \
                               any(any(c in cell for c in DESC_COL_CANDIDATES) for cell in row_str):
                                header_idx = idx
                                cols_lower = {i: str(cell).strip().lower() for i, cell in enumerate(row) if cell}
                                break
                                
                        if header_idx is None:
                            continue
                            
                        # Map columns
                        date_col_idx = None
                        desc_col_idx = None
                        debit_col_idx = None
                        credit_col_idx = None
                        amount_col_idx = None
                        
                        for i, col_name in cols_lower.items():
                            if any(cand in col_name for cand in DATE_COL_CANDIDATES):
                                date_col_idx = i
                            elif any(cand in col_name for cand in DESC_COL_CANDIDATES):
                                desc_col_idx = i
                            elif any(cand in col_name for cand in DEBIT_COL_CANDIDATES):
                                debit_col_idx = i
                            elif any(cand in col_name for cand in CREDIT_COL_CANDIDATES):
                                credit_col_idx = i
                            elif any(cand in col_name for cand in AMOUNT_COL_CANDIDATES):
                                amount_col_idx = i
                                
                        if date_col_idx is None or desc_col_idx is None:
                            continue
                            
                        # Parse data rows
                        for row in table[header_idx + 1:]:
                            if not row or len(row) <= max(date_col_idx, desc_col_idx):
                                continue
                                
                            raw_date = row[date_col_idx]
                            txn_date = parse_flexible_date(raw_date)
                            if not txn_date:
                                continue
                                
                            desc = str(row[desc_col_idx]).strip() if row[desc_col_idx] else ""
                            if not desc:
                                continue
                                
                            amt = 0.0
                            txn_type = "debit"
                            
                            if debit_col_idx is not None and len(row) > debit_col_idx and row[debit_col_idx]:
                                try:
                                    val = float(str(row[debit_col_idx]).replace(",", "").strip())
                                    if val > 0:
                                        amt = val
                                        txn_type = "debit"
                                except ValueError:
                                    pass
                                    
                            if credit_col_idx is not None and len(row) > credit_col_idx and row[credit_col_idx]:
                                try:
                                    val = float(str(row[credit_col_idx]).replace(",", "").strip())
                                    if val > 0:
                                        amt = val
                                        txn_type = "credit"
                                except ValueError:
                                    pass
                                    
                            if amt == 0.0 and amount_col_idx is not None and len(row) > amount_col_idx and row[amount_col_idx]:
                                try:
                                    val = float(str(row[amount_col_idx]).replace(",", "").strip())
                                    amt = abs(val)
                                    txn_type = "credit" if val > 0 else "debit"
                                except ValueError:
                                    pass
                                    
                            if amt == 0.0:
                                continue
                                
                            merchant, payment_mode = extract_merchant_and_mode(desc)
                            
                            transactions.append({
                                "date": txn_date,
                                "amount": round(amt, 2),
                                "type": txn_type,
                                "description": desc,
                                "raw_text": f"PDF_TABLE_ROW: {row}",
                                "merchant_name": merchant,
                                "payment_mode": payment_mode
                            })
                            
        except PDFPasswordIncorrect:
            raise PasswordProtectedPDFError("PDF is password-protected or password supplied is incorrect.")
        except Exception as e:
            if "password" in str(e).lower() or "encrypted" in str(e).lower():
                raise PasswordProtectedPDFError("PDF is password-protected or password supplied is incorrect.")
            raise e
            
        return transactions
