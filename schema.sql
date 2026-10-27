CREATE TABLE bis_registrations (
  id SERIAL PRIMARY KEY,
  reg_number TEXT NOT NULL,
  reg_number_norm TEXT NOT NULL UNIQUE,
  manufacturer TEXT,
  manufacturer_address TEXT,
  country TEXT,
  product_name TEXT,
  is_standard_raw TEXT,
  is_standard_key TEXT,
  is_standard_year INT,
  category TEXT,
  grant_date DATE,
  valid_to DATE,
  status TEXT CHECK (status IN ('registered','expired','deferred')),
  brands TEXT[],
  source_sn INT,
  raw JSONB,
  collected_on DATE,
  last_verified_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ON bis_registrations (is_standard_key);
CREATE INDEX ON bis_registrations USING GIN (brands);

CREATE TABLE scans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  image_key TEXT,
  ocr_text TEXT,
  extracted_reg_no TEXT,
  ocr_confidence REAL,
  channel TEXT DEFAULT 'web',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE verdicts (
  id SERIAL PRIMARY KEY,
  scan_id UUID REFERENCES scans(id),
  verdict TEXT CHECK (verdict IN ('green','amber','red')),
  reason_code TEXT NOT NULL,
  match_id INT REFERENCES bis_registrations(id),
  confidence REAL,
  decided_by TEXT DEFAULT 'auto',
  created_at TIMESTAMPTZ DEFAULT now()
);