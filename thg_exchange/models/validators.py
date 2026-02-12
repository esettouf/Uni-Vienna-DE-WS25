import re

def is_email(value: str) -> bool:
    if not value:
        return False
    v = value.strip().lower()
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v, re.IGNORECASE))
