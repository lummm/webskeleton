CREATE OR REPLACE FUNCTION verify_email(
  IN   p_email      TEXT
)
RETURNS BOOLEAN
AS $$
BEGIN
  RETURN p_email ~* '[A-Z0-9._%-]+@[A-Z0-9._%-]+\.[A-Z]{2,4}';
END;
$$
LANGUAGE plpgsql
;
