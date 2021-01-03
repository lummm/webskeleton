CREATE OR REPLACE FUNCTION sys.user_license_set_granted(
  IN p_user_id  UUID,
  IN p_license_id  UUID,
  IN p_quantity  INTEGER
)
RETURNS INTEGER
AS $$
BEGIN
  IF (SELECT 1
        FROM user_license
       WHERE user_id = p_user_id
         AND license_id = p_license_id) IS NULL THEN
    INSERT INTO user_license (
                  user_id,
                  license_id,
                  quantity
                )
         VALUES (
                  p_user_id,
                  p_license_id,
                  p_quantity
                )
    ;
    RETURN 1;
  ELSE
    UPDATE user_license
       SET quantity = p_quantity
     WHERE user_id = p_user_id
       AND license_id = p_license_id
    ;
    RETURN 0;
  END IF;
END;
$$
LANGUAGE plpgsql
;
