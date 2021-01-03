CREATE OR REPLACE FUNCTION dbg_dump_table(
  p_table_name  TEXT
)
RETURNS JSONB
AS $$
DECLARE
  v_res  JSONB;
BEGIN
  EXECUTE '
    SELECT jsonb_agg(' || p_table_name || ')
      FROM ' || p_table_name || '
  '
  INTO v_res
  ;
  RAISE NOTICE '
-------- %
%
---------', p_table_name, jsonb_pretty(v_res);
  RETURN v_res;
END;
$$
LANGUAGE plpgsql
;


CREATE OR REPLACE FUNCTION dbg_dump_tables()
RETURNS JSON
AS $$
DECLARE
  v_res  JSON  := '{}'::JSON;
  v_tables  TEXT[];
  v_name  TEXT;
BEGIN
  FOR v_name IN (
    SELECT table_name
      FROM information_schema.tables
     WHERE table_schema = 'public'
       AND table_type = 'BASE TABLE'  ) LOOP
    v_res := json_merge(v_res, json_build_object(
                                v_name, dbg_dump_table(v_name)::JSON
                              ));
  END LOOP;
  RETURN jsonb_pretty(v_res::JSONB)::JSON;
END;
$$
LANGUAGE plpgsql
;
