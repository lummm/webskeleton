CREATE OR REPLACE VIEW user_permissions
AS
       SELECT
     DISTINCT u.user_id,
              ap.permission_name
         FROM ac_user u
         JOIN ac_user_role ur
           ON ur.user_id = u.user_id
         JOIN ac_role_permission rp
           ON rp.role_id = ur.role_id
         JOIN ac_permission ap
           ON ap.permission_id = rp.permission_id
;
