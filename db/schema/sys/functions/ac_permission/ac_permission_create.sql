CREATE OR REPLACE FUNCTION sys.ac_permission_create(
  IN p_permission_name  TEXT
)
RETURNS UUID
AS $$
DECLARE
  v_permission_id  UUID  := new_uuid();
BEGIN
  INSERT INTO ac_permission (
                permission_id,
                permission_name
              )
       VALUES (
                v_permission_id,
                p_permission_name
              )
  ;
  RETURN v_permission_id;
END;
$$
LANGUAGE plpgsql
;
