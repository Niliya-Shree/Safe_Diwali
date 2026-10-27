import re
from dataclasses import dataclass

# OCR confusables: letters that look like digits
_CONFUSABLE = {"O": "0", "I": "1", "L": "1", "S": "5", "B": "8", "Z": "2"}

_PATTERN = re.compile(
    r"(?<![A-Z0-9])R[\s\-\u2013\u2014.:_]{0,3}([0-9OILSBZ]{8})(?![0-9OILSBZ])",
    re.IGNORECASE,
)

@dataclass(frozen=True)
class Candidate:
    reg: str        # canonical, e.g. "R-51002089"
    raw: str        # text exactly as matched
    repaired: bool  # True if letters were converted to digits

def extract_bis_candidates(ocr_text: str) -> list[Candidate]:
    seen, out = set(), []
    for m in _PATTERN.finditer(ocr_text or ""):
        token = m.group(1).upper()
        real_digits = sum(c.isdigit() for c in token)
        if real_digits < 6:          # too noisy: likely a random word
            continue
        digits = "".join(_CONFUSABLE.get(c, c) for c in token)
        reg = f"R-{digits}"
        if reg in seen:
            continue
        seen.add(reg)
        out.append(Candidate(reg=reg, raw=m.group(0), repaired=real_digits < 8))
    return out