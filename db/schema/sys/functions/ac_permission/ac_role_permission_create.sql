CREATE OR REPLACE FUNCTION sys.ac_role_permission_create(
  IN p_role_name  TEXT,
  IN p_permission_name  TEXT
)
RETURNS INTEGER
AS $$
DECLARE
  v_permission_id  UUID;
  v_role_id  UUID;
BEGIN
  SELECT permission_id
    INTO v_permission_id
    FROM ac_permission
   WHERE permission_name = p_permission_name
  ;
  SELECT role_id
    INTO v_role_id
    FROM ac_role
   WHERE role_name = p_role_name
  ;

  INSERT INTO ac_role_permission (
                role_id,
                permission_id
              )
       VALUES (
                v_role_id,
                v_permission_id
              )
  ;
  RETURN 1;
END;
$$
LANGUAGE plpgsql
;
