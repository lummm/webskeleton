CREATE OR REPLACE FUNCTION sys.license_create(
  IN p_license_code  TEXT,
  IN p_adhoc  JSONB  DEFAULT NULL
)
RETURNS UUID
AS $$
DECLARE
  v_license_id  UUID  := new_uuid();
BEGIN
  INSERT INTO license (
                license_id,
                license_code,
                adhoc
              )
       VALUES (
                v_license_id,
                p_license_code,
                p_adhoc
              )
  ;
  RETURN v_license_id;
END;
$$
LANGUAGE plpgsql
;
