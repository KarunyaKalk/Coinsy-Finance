import re

def mask_account_numbers(text: str) -> str:
    """
    Masks 10-18 digit bank account numbers and 16-digit card numbers in text strings,
    leaving only the last 4 digits visible.
    """
    if not text:
        return text

    # Pattern for 16-digit card numbers (optionally space or hyphen separated)
    def mask_card(match):
        digits = re.sub(r'\D', '', match.group(0))
        if len(digits) == 16:
            return f"XXXX-XXXX-XXXX-{digits[-4:]}"
        return match.group(0)

    text = re.sub(r'\b(?:\d[ -]*?){16}\b', mask_card, text)

    # Pattern for 10-18 digit account numbers (e.g. A/C 50100123456789)
    def mask_acct(match):
        digits = match.group(0)
        if len(digits) >= 10:
            masked = "X" * (len(digits) - 4) + digits[-4:]
            return masked
        return digits

    # Look for 10-18 consecutive digits
    text = re.sub(r'\b\d{10,18}\b', mask_acct, text)

    return text
