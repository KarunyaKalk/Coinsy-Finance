from typing import List, Dict, Any, Optional
from app.services.pdf_parser.base import BaseBankPDFParser, PasswordProtectedPDFError, PDFParsingError
from app.services.pdf_parser.generic_table_parser import GenericTablePDFParser
from app.services.pdf_parser.llm_pdf_parser import LLMAssistedPDFParser
from app.services.pdf_parser.masking import mask_account_numbers

class PDFStatementManager:
    def __init__(self):
        self.parsers: List[BaseBankPDFParser] = [
            GenericTablePDFParser(),
            LLMAssistedPDFParser()
        ]

    def add_parser(self, parser: BaseBankPDFParser):
        """Allows registering additional bank-specific parsers at runtime."""
        self.parsers.insert(0, parser)

    def parse_pdf_statement(self, pdf_bytes: bytes, password: Optional[str] = None) -> List[Dict[str, Any]]:
        transactions = []
        
        for parser in self.parsers:
            try:
                parsed = parser.parse(pdf_bytes, password=password)
                if parsed:
                    transactions = parsed
                    break
            except PasswordProtectedPDFError as e:
                raise e
            except Exception:
                continue

        # Mask full account numbers across all extracted transaction fields
        for tx in transactions:
            tx["description"] = mask_account_numbers(tx.get("description", ""))
            if tx.get("merchant_name"):
                tx["merchant_name"] = mask_account_numbers(tx["merchant_name"])
            if tx.get("raw_text"):
                tx["raw_text"] = mask_account_numbers(tx["raw_text"])

        return transactions

pdf_statement_manager = PDFStatementManager()
