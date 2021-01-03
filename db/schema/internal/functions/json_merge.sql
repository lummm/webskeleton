CREATE OR REPLACE FUNCTION json_merge(
  IN p_target  JSON,
  IN p_merge_in  JSON
)
RETURNS JSON
AS $$
BEGIN
  RETURN jsonb_merge(p_target::JSONB, p_merge_in::JSONB)::JSON;
END;
$$
LANGUAGE plpgsql
;
