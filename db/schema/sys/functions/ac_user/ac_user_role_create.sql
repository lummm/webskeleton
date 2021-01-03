CREATE OR REPLACE FUNCTION sys.ac_user_role_create(
  IN p_user_id  UUID,
  IN p_role_name  TEXT
)
RETURNS UUID
AS $$
DECLARE
  v_role_id  UUID;
BEGIN
  SELECT role_id
    INTO v_role_id
    FROM ac_role
   WHERE role_name = p_role_name
  ;
  INSERT INTO ac_user_role (
                user_id,
                role_id
              )
       VALUES (
                p_user_id,
                v_role_id
              )
  ;
  RETURN v_role_id;
END;
$$
LANGUAGE plpgsql
;
