CREATE TABLE bis_registrations (
  id SERIAL PRIMARY KEY,
  reg_number TEXT NOT NULL,                 -- R-51000019
  reg_number_norm TEXT NOT NULL UNIQUE,     -- R51000019
  manufacturer TEXT,
  manufacturer_address TEXT,
  country TEXT,
  product_name TEXT,
  is_standard_raw TEXT,
  is_standard_key TEXT,                     -- IS10322-P5-S7
  is_standard_year INT,
  category TEXT,                            -- lighting_chain / led_lamp / other
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