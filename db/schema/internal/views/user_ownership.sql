CREATE OR REPLACE VIEW user_ownership
AS
     SELECT uo.user_id,
            uo.object_id obj_id
       FROM user_object uo
;
