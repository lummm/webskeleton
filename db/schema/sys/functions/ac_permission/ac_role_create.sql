CREATE OR REPLACE FUNCTION sys.ac_role_create(
  IN p_role_name  TEXT
)
RETURNS UUID
AS $$
DECLARE
  v_role_id  UUID  := new_uuid();
BEGIN
  INSERT INTO ac_role (
                role_id,
                role_name
              )
       VALUES (
                v_role_id,
                p_role_name
              )
  ;
  RETURN v_role_id;
END;
$$
LANGUAGE plpgsql
;
