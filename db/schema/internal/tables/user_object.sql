CREATE TABLE IF NOT EXISTS user_object (
  object_id  UUID   NOT NULL
    REFERENCES object (object_id),
  user_id  UUID  NOT NULL
    REFERENCES ac_user (user_id),

  PRIMARY KEY (object_id, user_id)
);
