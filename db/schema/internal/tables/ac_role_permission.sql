CREATE TABLE IF NOT EXISTS ac_role_permission (
  role_id  UUID   NOT NULL
    REFERENCES ac_role (role_id)  ON DELETE CASCADE,
  permission_id  UUID  NOT NULL
    REFERENCES ac_permission (permission_id)  ON DELETE CASCADE,

  PRIMARY KEY (role_id, permission_id)
);
