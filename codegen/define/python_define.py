"""
# this expects the json(b) decoder to be as such:
await conn.set_type_codec(
            'json',
            encoder=json.dumps,
            decoder=json.loads,
            schema='pg_catalog'
        )
"""
from typez import DefineLang, FnArg, FnRecord, TableRecord


def _get_calling_sql(schema: str, fn: FnRecord) -> str:
    arg_sql = ",\n      ".join([
        f"{fn.args[i].name} => ${i + 1}::{fn.args[i].type}"
        for i in range(len(fn.args))
    ])
    bindargs = ", ".join([arg.name for arg in fn.args])
    return f"""return await db.fetch_val(\"\"\"
    SELECT {schema}.{fn.name}(
      {arg_sql}
    )
    \"\"\", ({bindargs}))"""


def _type_lookup(typename: str) -> str:
    typemap = {
        "text": "str",
        "integer": "int",
        "uuid": "str",
        "json": "Dict",
        "jsonb": "Dict",
        "boolean": "bool",
        "bytea": "bytes",
    }
    if len(typename) > 2 and typename[-2:] == "[]":
        item_type = typemap[typename[:-2]]
        return f"List[{item_type}]"
    return typemap[typename]


def _get_fn_args(fn: FnRecord) -> str:
    def fmt_arg(arg: FnArg) -> str:
        arg_type = _type_lookup(arg.type)
        if arg.default is None:
            return f"{arg.name}: {arg_type}"
        new_default = arg.default
        if arg.default == "NULL":
            new_default = "None"
        return f"{arg.name}: {arg_type} = {new_default}"
    return ", ".join([fmt_arg(arg) for arg in fn.args])


def get_impl_language_fn_def(schema: str, fn: FnRecord) -> str:
    calling_sql = _get_calling_sql(schema, fn)
    impl_fn_args = _get_fn_args(fn)
    ret_type = _type_lookup(fn.ret_type)
    impl = f"""async def {fn.name}({impl_fn_args}) -> {ret_type}:
    {calling_sql}

"""
    return impl


def _snake_case_to_camel(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))


def get_impl_language_model_def(schema: str, view: TableRecord):
    nt_name = _snake_case_to_camel(view.name)
    props = [f"{col.name}: {_type_lookup(col.type)}" for col in view.columns]
    props_content = "\n    ".join(props)
    named_tuple = f"""class {nt_name}(NamedTuple):
    {props_content}
"""
    column_content = "\n    ".join([f"'{col.name}': {view.name}_table.{col.name}," for col in view.columns])
    columns = f"""{view.name}_table = Table("{schema}.{view.name}")
{view.name} = Box({{
    'table_ref': {view.name}_table,
    'get_query': lambda: PostgreSQLQuery.from_({view.name}_table),
    {column_content}
}})"""
    return f"""{named_tuple}

{columns}"""


def wrap_view_defs(contents: str) -> str:
    return f"""from typing import NamedTuple, List, Dict

from box import Box             # type: ignore
from pypika import Table, PostgreSQLQuery, Schema # type: ignore


# views = Schema("sys")

{contents}
"""


def wrap_fn_defs(contents: str) -> str:
    return f"""from typing import Dict, List

import webskeleton.db as db


{contents}
"""
