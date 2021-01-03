CREATE TABLE IF NOT EXISTS ac_user (
  user_id  UUID   NOT NULL  DEFAULT uuid_generate_v1mc(),
  created  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  updated  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  email_lower  TEXT  NOT NULL,
  pw_hash  TEXT,
  adhoc  JSONB  DEFAULT NULL,

  PRIMARY KEY (user_id),
  UNIQUE (email_lower)
);
