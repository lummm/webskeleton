import os
from typing import List, NamedTuple, Tuple, Optional, Any

import psycopg2

from typez import FnArg, FnRecord, TableRecord, ColumnRecord


RawFn = Tuple[str, str]
RawView = Tuple[str, str]


con = None


def _to_fn_arg(arg_row: List[str])-> FnArg:
    if len(arg_row) == 2:
        # [<var_name>, <var_type>]
        return FnArg(name=arg_row[0], type=arg_row[1])
    # [<var_name>, <var_type>, DEFAULT, <default_val::type>]
    if 'DEFAULT' != arg_row[2]:
        print(arg_row)
        raise Exception("failed to parse fn" + str(arg_row))
    default = arg_row[3].split("::")[0]
    return FnArg(
        name=arg_row[0],
        type=arg_row[1],
        default=default
    )


def _parse_raw_fn(raw: RawFn) -> FnRecord:
    name = raw[0]
    ret_type = raw[1]
    args = [a.split(" ") for a in raw[2].split(", ")]
    fn_args = [_to_fn_arg(a) for a in args]
    return FnRecord(
        name=name,
        ret_type=ret_type,
        args=fn_args,
    )


def _parse_raw_table(raw: RawView) -> TableRecord:
    columns = [ColumnRecord(name=r["name"], type=r["type"])
               for r in raw[1]]
    return TableRecord(
        name=raw[0],
        columns=columns,
    )


def _fetch_schema_functions(
        cur, schema: str
) -> List[RawFn]:
    sql = """
      SELECT p.proname fn_name,
             pg_get_function_result(p.oid),
             pg_get_function_arguments(p.oid) args
        FROM pg_proc p
        JOIN pg_namespace ns
          ON (p.pronamespace = ns.oid)
       WHERE ns.nspname = %s;
    """
    cur.execute(sql, [schema])
    return cur.fetchall()


def _fetch_schema_views(
        cur, schema: str
):
    sql = """
    select t.table_name as view_name,
           json_agg(json_build_object(
             'name', c.column_name,
             'type', c.data_type
           ))
      from information_schema.tables t
 left join information_schema.columns c
        on t.table_schema = c.table_schema
       and t.table_name = c.table_name
     where table_type = 'VIEW'
       and t.table_schema = %s
     group by t.table_name
    ;
    """
    cur.execute(sql, [schema])
    return cur.fetchall()


def _with_cur(fn):
    def impl(*args, **kwargs):
        cur = con.cursor()
        try:
            res = fn(cur, *args, **kwargs)
        finally:
            cur.close()
        return res
    return impl


def connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        user=os.getenv("PGUSER", "postgres"),
        dbname=os.getenv("PGDB", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
        port=int(os.getenv("PGPORT", "5432")),
) -> None:
    global con
    con = psycopg2.connect(
        host=host,
        user=user,
        dbname=dbname,
        password=password,
        port=port,
    )
    return


def shutdown():
    con.close()
    return


def load_schema_functions(schema: str) -> List[FnRecord]:
    raw_fns = _with_cur(_fetch_schema_functions)(schema)
    return [_parse_raw_fn(f) for f in raw_fns]


def load_schema_views(schema: str) -> List[TableRecord]:
    raw_views = _with_cur(_fetch_schema_views)(schema)
    return [_parse_raw_table(f) for f in raw_views]
