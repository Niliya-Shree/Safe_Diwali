import sys, datetime as dt
import pandas as pd, psycopg
from psycopg.types.json import Jsonb
sys.path.insert(0, "api")
from app.normalize import canonical_reg, normalize_reg, parse_is, CATEGORY

DB = "postgresql://safe:safe@localhost:5432/safediwali"
RAW_COLS = ["S No", "Registration Number", "Name of manufacturer", "Address of manufacturer",
            "Country", "Product name", "IS number", "Date of grant of licence",
            "Status", "Validity", "Scope of licence", "Brand"]
STATUSES = {"registered", "expired", "deferred"}

def d(s):
    return pd.to_datetime(s, format="%d-%m-%Y", errors="coerce")

def main(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    rows, rejects, seen = [], [], set()
    for _, r in df.iterrows():
        reg = canonical_reg(r["Registration Number"])
        status = r["Status"].strip().lower()
        grant, valid = d(r["Date of grant of licence"]), d(r["Validity"])
        key, year = parse_is(r["IS number"])
        reason = None
        if not reg: reason = "bad_reg_format"
        elif normalize_reg(reg) in seen: reason = "duplicate"
        elif status not in STATUSES: reason = f"bad_status:{status}"
        elif pd.isna(valid): reason = "bad_validity_date"
        elif not key: reason = "unparsed_is_standard"
        if reason:
            rejects.append({**r[RAW_COLS].to_dict(), "reject_reason": reason}); continue
        seen.add(normalize_reg(reg))
        brands = [b.strip() for b in r["Brand"].split(",") if b.strip()]
        rows.append((reg, normalize_reg(reg), r["Name of manufacturer"], r["Address of manufacturer"],
                     r["Country"], r["Product name"], r["IS number"], key, year,
                     CATEGORY.get(key, "other"),
                     None if pd.isna(grant) else grant.date(), valid.date(), status, brands,
                     int(r["S No"]) if r["S No"].isdigit() else None,
                     Jsonb(r[RAW_COLS].to_dict()), dt.date.today()))
    with psycopg.connect(DB) as conn, conn.cursor() as cur:
        cur.executemany("""
          INSERT INTO bis_registrations
          (reg_number, reg_number_norm, manufacturer, manufacturer_address, country, product_name,
           is_standard_raw, is_standard_key, is_standard_year, category, grant_date, valid_to,
           status, brands, source_sn, raw, collected_on)
          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
          ON CONFLICT (reg_number_norm) DO UPDATE SET
            status=EXCLUDED.status, valid_to=EXCLUDED.valid_to,
            raw=EXCLUDED.raw, last_verified_at=now()""", rows)
    pd.DataFrame(rejects).to_csv("data/clean/rejected.csv", index=False)
    print(f"loaded={len(rows)} rejected={len(rejects)}")
    if rejects:
        print(pd.DataFrame(rejects)["reject_reason"].value_counts())

if __name__ == "__main__":
    main(sys.argv[1])