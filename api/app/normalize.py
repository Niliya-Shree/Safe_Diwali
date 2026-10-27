import re

def normalize_reg(s: str) -> str:
    """'R-51000019' / 'r 51000019' -> 'R51000019' (for matching)"""
    return re.sub(r"[\s\-_.]", "", (s or "").upper().strip())

def canonical_reg(s: str) -> str | None:
    """Returns 'R-51000019' or None if format is invalid."""
    m = re.fullmatch(r"R(\d{8})", normalize_reg(s))
    return f"R-{m.group(1)}" if m else None

_IS_RE = re.compile(
    r"IS\s*(\d+)\s*(?:\(\s*PART\s*(\d+)\s*(?:/\s*SEC\s*(\d+))?\s*\))?\s*:\s*(\d{4})",
    re.I,
)

def parse_is(s: str):
    """'IS 10322 (Part 5/Sec 7) : 2017 / IEC ...' -> ('IS10322-P5-S7', 2017)"""
    m = _IS_RE.search(s or "")
    if not m:
        return None, None
    num, part, sec, year = m.groups()
    key = f"IS{num}" + (f"-P{part}" if part else "") + (f"-S{sec}" if sec else "")
    return key, int(year)

# Isse pehle tumhari unique IS list se verify karo, phir bharo.
CATEGORY = {
    "IS10322-P5-S7": "lighting_chain",
    "IS10322-P5-S3": "street_light",
    "IS10322-P5-S8": "emergency_light",
    "IS16102-P1": "led_lamp",
    "IS16103-P1": "led_module",
}