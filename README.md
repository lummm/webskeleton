# WEBSKELETON

This is intended to get you off the ground with an http server and postgres connection
as fast as possible.

Focus is on speed of development and stying out of the way so you can prototype.
I'll do some performance benchmarks eventually.

## Assumptions
- You're using postgres
- you have a view defined called 'user_ownership' that has two UUID columns:
  'user_id' and 'obj_id', where an entry means that a user owns a given object.
- you're using redis
- configuration is mostly through the env - see [env.py](./webskeleton/env.py)
