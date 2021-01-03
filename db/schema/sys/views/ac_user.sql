CREATE OR REPLACE VIEW sys.ac_user
AS
  SELECT user_id,
         unix_ts(created) created,
         unix_ts(updated) updated,
         email_lower,
         pw_hash,
         adhoc
    FROM ac_user
;
