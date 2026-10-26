from app.normalize import canonical_reg, parse_is

def test_canonical():
    assert canonical_reg("R-51000019") == "R-51000019"
    assert canonical_reg("r 51000019") == "R-51000019"
    assert canonical_reg("R-5100001") is None      # 7 digits
    assert canonical_reg("CM/L-1234567") is None

def test_parse_is():
    assert parse_is("IS 16102 (Part 1) : 2012") == ("IS16102-P1", 2012)
    assert parse_is("IS 10322 (Part 5/Sec 7) : 2017 / IEC 60598-2-20 : 2014") == ("IS10322-P5-S7", 2017)
    assert parse_is("IS 16103 (Part 1): 2025/ IEC 62031: 2018") == ("IS16103-P1", 2025)