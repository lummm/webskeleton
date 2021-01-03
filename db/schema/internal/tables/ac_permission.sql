CREATE TABLE IF NOT EXISTS ac_permission (
  permission_id  UUID   NOT NULL  DEFAULT uuid_generate_v1mc(),
  permission_name  TEXT  NOT NULL,

  PRIMARY KEY (permission_id),
  UNIQUE (permission_name)
);
