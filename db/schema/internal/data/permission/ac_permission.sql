DO $$
DECLARE
  v_roles  TEXT[]  := ARRAY['USER'];
  v_role  TEXT;
  v_row  JSON;
  v_permissions  JSON[]  := ARRAY[
    json_build_object(
      'name', 'empty',
      'roles', json_build_array()
    )
  ];
  v_permission  JSON;
BEGIN
  DELETE FROM ac_role;
  FOREACH v_role IN ARRAY v_roles LOOP
    PERFORM sys.ac_role_create(p_role_name => v_role);
  END LOOP;

  DELETE FROM ac_permission;
  FOREACH v_permission IN ARRAY v_permissions LOOP
    PERFORM sys.ac_permission_create(p_permission_name => v_permission->>'name');
    FOR i IN 1..json_array_length(v_permission->'roles') LOOP
      v_role := (v_permission->'roles')->>(i - 1);
      PERFORM sys.ac_role_permission_create(
        p_role_name => v_role,
        p_permission_name => v_permission->>'name'
      );
    END LOOP;
  END LOOP;

END;
$$ LANGUAGE plpgsql;
