from dataclasses import dataclass, field
from datetime import date

from .extract import Candidate

OCR_CONF_MIN = 0.70  # tune later with real photos


@dataclass(frozen=True)
class Record:
    reg: str                 # "R-51002089"
    status: str              # registered / expired / deferred
    valid_to: date
    category: str            # lighting_chain, street_light, ...
    brands: tuple[str, ...] = ()
    manufacturer: str = ""


@dataclass(frozen=True)
class Verdict:
    verdict: str             # green / amber / red
    reason: str              # strict reason code
    reg: str | None = None
    record: Record | None = None
    needs_review: bool = False
    detail: dict = field(default_factory=dict)


def _v(verdict, reason, rec=None, reg=None, review=False, **detail):
    return Verdict(verdict, reason, reg or (rec.reg if rec else None), rec, review, detail)


def decide(
    candidates: list[Candidate],
    records: dict[str, Record],          # only records for these candidates
    today: date,
    ocr_confidence: float = 1.0,
    expected_category: str = "lighting_chain",
) -> Verdict:
    # 1. Nothing found
    if not candidates:
        if ocr_confidence < OCR_CONF_MIN:
            return _v("amber", "LOW_QUALITY_IMAGE", review=True)
        return _v("red", "NO_NUMBER_FOUND")

    # 2. Which candidates exist in the DB?
    found = [c for c in candidates if c.reg in records]
    if not found:
        # DB is only a partial copy of BIS data -> never Red here
        return _v("amber", "NUMBER_NOT_IN_DB", reg=candidates[0].reg, review=True)

    if len(found) > 1:
        same_cat = [c for c in found if records[c.reg].category == expected_category]
        if len(same_cat) != 1:
            return _v("amber", "MULTIPLE_MATCHES", review=True,
                      regs=[c.reg for c in found])
        found = same_cat

    cand = found[0]
    rec = records[cand.reg]

    # 3. Status / validity (Red only when we are sure)
    if rec.status == "expired" or rec.valid_to < today:
        return _v("red", "EXPIRED", rec, valid_to=str(rec.valid_to))
    if rec.status == "deferred":
        return _v("amber", "STATUS_DEFERRED", rec, review=True)
    if rec.status != "registered":
        return _v("amber", "UNKNOWN_STATUS", rec, review=True)

    # 4. Doubt checks -> Amber
    if rec.category != expected_category:
        return _v("amber", "CATEGORY_MISMATCH", rec, review=True,
                  registered_as=rec.category, expected=expected_category)
    if cand.repaired:
        return _v("amber", "OCR_REPAIRED", rec, review=True)
    if ocr_confidence < OCR_CONF_MIN:
        return _v("amber", "LOW_OCR_CONFIDENCE", rec, review=True)

    # 5. Only now: Green
    return _v("green", "VALID_MATCH", rec)