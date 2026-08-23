from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class PasswordProtectedPDFError(Exception):
    """Raised when PDF is encrypted and requires a password or provided password is invalid."""
    pass

class PDFParsingError(Exception):
    """Raised when PDF parsing fails."""
    pass

class BaseBankPDFParser(ABC):
    @abstractmethod
    def parse(self, pdf_bytes: bytes, password: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Parses PDF bytes and returns a list of normalized transaction dictionaries.
        """
        pass
