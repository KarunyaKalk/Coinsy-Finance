import io
import json
import logging
import re
from typing import List, Dict, Any, Optional
import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect
import anthropic
from app.core.config import settings
from app.services.pdf_parser.base import BaseBankPDFParser, PasswordProtectedPDFError
from app.services.csv_parser import parse_flexible_date, extract_merchant_and_mode

logger = logging.getLogger(__name__)

def fallback_text_regex_parser(text: str) -> List[Dict[str, Any]]:
    """
    Heuristic regex parser that scans unformatted text lines for date and amount patterns.
    """
    transactions = []
    lines = text.splitlines()
    
    # Pattern e.g. 23/08/2026 or 23-Aug-2026 or 2026-08-23 followed by description and amount
    pattern = r'(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2}|\d{1,2}[-\s][A-Za-z]{3}[-\s]\d{4})\s+(.+?)\s+([\d,]+\.\d{2})'
    
    for line in lines:
        line_str = line.strip()
        match = re.search(pattern, line_str)
        if match:
            date_str, desc, amt_str = match.groups()
            txn_date = parse_flexible_date(date_str)
            if not txn_date:
                continue
            try:
                amt = float(amt_str.replace(",", ""))
            except ValueError:
                continue
                
            txn_type = "debit"
            if "cr" in line_str.lower() or "credit" in line_str.lower() or "deposit" in line_str.lower():
                txn_type = "credit"
                
            merchant, payment_mode = extract_merchant_and_mode(desc)
            
            transactions.append({
                "date": txn_date,
                "amount": round(amt, 2),
                "type": txn_type,
                "description": desc.strip(),
                "raw_text": f"PDF_TEXT_LINE: {line_str}",
                "merchant_name": merchant,
                "payment_mode": payment_mode
            })
            
    return transactions

class LLMAssistedPDFParser(BaseBankPDFParser):
    def parse(self, pdf_bytes: bytes, password: Optional[str] = None) -> List[Dict[str, Any]]:
        extracted_text = ""
        
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes), password=password) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text()
                    if txt:
                        extracted_text += txt + "\n"
        except PDFPasswordIncorrect:
            raise PasswordProtectedPDFError("PDF is password-protected or password supplied is incorrect.")
        except Exception as e:
            if "password" in str(e).lower() or "encrypted" in str(e).lower():
                raise PasswordProtectedPDFError("PDF is password-protected or password supplied is incorrect.")
            raise e

        if not extracted_text.strip():
            return []

        # If Anthropic API Key is absent, fallback to regex text parser
        if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.strip() == "":
            logger.info("No ANTHROPIC_API_KEY configured for PDF LLM parser. Using regex text fallback.")
            return fallback_text_regex_parser(extracted_text)

        # Prompt Claude API to extract structured JSON from raw PDF text
        system_prompt = (
            "You are Coinsy PDF Statement Parser. Extract financial transactions from unformatted bank statement text. "
            "Return ONLY a valid JSON array of objects with keys: 'date' (YYYY-MM-DD), 'amount' (float > 0), "
            "'type' ('debit' or 'credit'), 'description' (string), and 'merchant_name' (optional string)."
        )

        user_prompt = (
            f"Extract all transactions from this bank statement text into JSON format:\n\n"
            f"{extracted_text[:12000]}\n\n"  # Trim to prevent exceeding context limit
            f"JSON Output:"
        )

        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                temperature=0.0,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            content_text = response.content[0].text.strip()
            if content_text.startswith("```"):
                content_text = content_text.split("```")[1]
                if content_text.startswith("json"):
                    content_text = content_text[4:]
            content_text = content_text.strip()

            parsed_items = json.loads(content_text)
            transactions = []

            for item in parsed_items:
                txn_date = parse_flexible_date(item.get("date"))
                if not txn_date:
                    continue
                amt = float(item.get("amount", 0.0))
                if amt <= 0:
                    continue
                    
                desc = item.get("description", "PDF Transaction")
                merchant = item.get("merchant_name")
                if not merchant:
                    merchant, _ = extract_merchant_and_mode(desc)
                    
                transactions.append({
                    "date": txn_date,
                    "amount": round(amt, 2),
                    "type": item.get("type", "debit").lower(),
                    "description": desc,
                    "raw_text": f"LLM_PDF_EXTRACT: {item}",
                    "merchant_name": merchant,
                    "payment_mode": "UPI"
                })

            return transactions

        except Exception as e:
            logger.error(f"Error in LLM PDF extraction: {e}. Falling back to regex text parser.")
            return fallback_text_regex_parser(extracted_text)
