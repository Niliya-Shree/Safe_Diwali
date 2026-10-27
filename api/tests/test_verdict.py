from datetime import date
from app.extract import Candidate
from app.verdict import Record, decide

TODAY = date(2026, 10, 27)

def rec(reg, status="registered", valid_to=date(2028, 1, 1), cat="lighting_chain"):
    return Record(reg, status, valid_to, cat, ("TESTBRAND",))

def cand(reg, repaired=False):
    return Candidate(reg, reg, repaired)

def run(cands, recs, **kw):
    return decide(cands, {r.reg: r for r in recs}, TODAY, **kw)

def test_green():
    v = run([cand("R-62005819")], [rec("R-62005819")])
    assert (v.verdict, v.reason) == ("green", "VALID_MATCH")

def test_no_number_clear_photo_is_red():
    assert run([], [], ocr_confidence=0.95).reason == "NO_NUMBER_FOUND"

def test_no_number_blurry_photo_is_amber_not_red():
    v = run([], [], ocr_confidence=0.3)
    assert (v.verdict, v.reason, v.needs_review) == ("amber", "LOW_QUALITY_IMAGE", True)

def test_number_not_in_db_is_amber_never_red():
    assert run([cand("R-99999999")], []).verdict == "amber"

def test_expired_status_is_red():
    v = run([cand("R-51001856")], [rec("R-51001856", "expired", date(2026, 6, 8))])
    assert (v.verdict, v.reason) == ("red", "EXPIRED")

def test_registered_but_date_passed_is_red():
    # status says registered, validity ended yesterday
    v = run([cand("R-1")], [rec("R-1", "registered", date(2026, 10, 26))])
    assert (v.verdict, v.reason) == ("red", "EXPIRED")

def test_valid_today_is_still_green():
    assert run([cand("R-1")], [rec("R-1", valid_to=TODAY)]).verdict == "green"

def test_deferred_is_amber():
    assert run([cand("R-1")], [rec("R-1", "deferred")]).reason == "STATUS_DEFERRED"

def test_category_mismatch_is_amber():
    v = run([cand("R-1")], [rec("R-1", cat="street_light")])
    assert (v.verdict, v.reason) == ("amber", "CATEGORY_MISMATCH")

def test_repaired_ocr_never_green():
    assert run([cand("R-1", repaired=True)], [rec("R-1")]).verdict == "amber"

def test_low_ocr_confidence_never_green():
    assert run([cand("R-1")], [rec("R-1")], ocr_confidence=0.5).verdict == "amber"

def test_two_matches_resolved_by_category():
    v = run([cand("R-1"), cand("R-2")], [rec("R-1", cat="led_lamp"), rec("R-2")])
    assert (v.verdict, v.reg) == ("green", "R-2")

def test_two_matches_same_category_is_amber():
    v = run([cand("R-1"), cand("R-2")], [rec("R-1"), rec("R-2")])
    assert v.reason == "MULTIPLE_MATCHES"

def test_real_record_expires_soon():
    # R-51002089 (Century/MAGIK) is valid till 2026-11-23
    r = rec("R-51002089", valid_to=date(2026, 11, 23))
    assert decide([cand("R-51002089")], {r.reg: r}, date(2026, 11, 23)).verdict == "green"
    assert decide([cand("R-51002089")], {r.reg: r}, date(2026, 11, 24)).reason == "EXPIRED"