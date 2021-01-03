CREATE TABLE IF NOT EXISTS user_license (
  user_id  UUID  NOT NULL
    REFERENCES ac_user (user_id)  ON DELETE CASCADE,
  license_id  UUID  NOT NULL  DEFAULT uuid_generate_v1mc()
    REFERENCES license (license_id)  ON DELETE CASCADE,
  quantity  INTEGER  DEFAULT 0,

  PRIMARY KEY (user_id, license_id)
);

COMMENT ON COLUMN user_license.quantity IS 'NULL is infinite.';
