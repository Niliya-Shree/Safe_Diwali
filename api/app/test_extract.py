import pytest
from app.extract import extract_bis_candidates

def regs(text):
    return [c.reg for c in extract_bis_candidates(text)]

@pytest.mark.parametrize("text", [
    "R-51002089", "R51002089", "R - 51002089", "r-51002089",
    "R-\n51002089", "Reg. No. R-51002089 Made in India",
])
def test_valid_formats(text):
    assert regs(text) == ["R-51002089"]

def test_ocr_noise_is_repaired_and_flagged():
    c = extract_bis_candidates("R-5I002O89")[0]
    assert c.reg == "R-51002089"
    assert c.repaired is True

def test_clean_number_is_not_flagged():
    assert extract_bis_candidates("R-62005819")[0].repaired is False

@pytest.mark.parametrize("text", [
    "", "Made in China 220V 5W", "Call 9876543210 Batch 20250101",
    "REGULAR LED 12V", "R-5100208", "R-510020891", "SR-51002089",
])
def test_no_match(text):
    assert regs(text) == []

def test_dedupe_and_multiple():
    assert regs("R-51002089 xx R51002089 yy R-62005819") == ["R-51002089", "R-62005819"]