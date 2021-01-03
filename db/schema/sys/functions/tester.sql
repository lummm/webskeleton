CREATE OR REPLACE FUNCTION sys.tester(
  IN p_thing  TEXT,
  IN p_thing_2  TEXT,
  IN p_thing_3  TEXT = 'hello'
)
RETURNS UUID
AS $$
BEGIN
  RETURN new_uuid();
END;
$$
LANGUAGE plpgsql
;
