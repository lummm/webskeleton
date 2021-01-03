CREATE TABLE IF NOT EXISTS license (
  license_id  UUID  NOT NULL  DEFAULT uuid_generate_v1mc(),
  license_code  TEXT  NOT NULL,
  adhoc  JSONB,

  PRIMARY KEY (license_id),
  UNIQUE (license_code)
);
