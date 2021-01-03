from typez import DefineLang, FnArg, FnRecord


def _get_calling_sql(schema: str, fn: FnRecord) -> str:
    arg_sql = ",\n      ".join([
        f"{fn.args[i].name} => ${fn.args[i].name}::{fn.args[i].type}"
        for i in range(len(fn.args))
    ])
    return f"""\"\"\"
    SELECT {schema}.{fn.name}(
      {arg_sql}
    )
    \"\"\""""

def _type_lookup(typename: str) -> str:
    return {
        "text": "String",
        "integer": "Int",
        "uuid": "String",
        "json": "String",
        "jsonb": "String",
    }[typename]


def _get_fn_args(fn: FnRecord) -> str:
    def fmt_arg(arg: FnArg) -> str:
        arg_type = _type_lookup(arg.type)
        if arg.default is None:
            return f"{arg.name}: {arg_type}"
        new_default = arg.default
        if arg.default == "NULL":
            new_default = "null"
        if len(arg.default) > 1 \
           and arg.default[0] == "'" \
           and arg.default[-1] == "'":
            new_default = "\"" + arg.default[1:-1] + "\""
        return f"{arg.name}: {arg_type} = {new_default}"
    arg_s = ", ".join([fmt_arg(arg) for arg in fn.args])
    return arg_s


def get_impl_language_fn_def(schema: str, fn: FnRecord) -> str:
    calling_sql = _get_calling_sql(schema, fn)
    impl_fn_args = _get_fn_args(fn)
    ret_type = _type_lookup(fn.ret_type)
    impl = f"""  def {fn.name}({impl_fn_args}) = sql{calling_sql}.as[{ret_type}]\n"""
    return impl


def wrap_fn_defs(contents: str) -> str:
    return f"""import slick.jdbc.PostgresProfile.api._

object DDB {{

{contents}
}}
"""
