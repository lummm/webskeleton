CREATE TABLE IF NOT EXISTS object (
  object_id  UUID   NOT NULL  DEFAULT uuid_generate_v1mc(),
  created  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  updated  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  adhoc  JSONB  DEFAULT NULL,

  PRIMARY KEY (object_id)
);
