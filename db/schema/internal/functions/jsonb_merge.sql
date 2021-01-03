CREATE OR REPLACE FUNCTION jsonb_merge(
  IN p_target  JSONB,
  IN p_merge_in  JSONB
)
RETURNS JSONB
AS $$
BEGIN
  IF p_target IS NULL THEN
    p_target := '{}'::JSONB;
  END IF;
  IF p_merge_in IS NULL THEN
    p_merge_in := '{}'::JSONB;
  END IF;
  RETURN p_target || p_merge_in;
END;
$$
LANGUAGE plpgsql
;
