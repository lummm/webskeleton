CREATE TABLE IF NOT EXISTS ac_role (
  role_id  UUID   NOT NULL  DEFAULT uuid_generate_v1mc(),
  role_name  TEXT  NOT NULL,

  PRIMARY KEY (role_id),
  UNIQUE (role_name)
);
