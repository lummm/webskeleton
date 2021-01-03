CREATE TABLE IF NOT EXISTS ac_user_role (
  user_id  UUID   NOT NULL
    REFERENCES ac_user (user_id)  ON DELETE CASCADE,
  role_id  UUID  NOT NULL
    REFERENCES ac_role (role_id)  ON DELETE CASCADE,

  PRIMARY KEY (user_id, role_id)
);
