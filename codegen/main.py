#!/usr/bin/env python3
"""
This dynamically generates function defintions
and types corresponding to views based on the db schema.
"""

import argparse

import db
import define
from typez import DefineLang, OutputObjType


parser = argparse.ArgumentParser()
parser.add_argument("--lang", type=DefineLang, help="output language")
parser.add_argument("--schema", type=str, help="db schema name")
parser.add_argument("--objtype", type=OutputObjType, help="db schema name")


def get_fns(args) -> str:
    fns = db.load_schema_functions(args.schema)
    return define.get_fn_def_file_contents(args.schema, args.lang, fns)


def get_views(args) -> str:
    fns = db.load_schema_views(args.schema)
    return define.get_view_def_file_contents(args.schema, args.lang, fns)


def main():
    args = parser.parse_args()
    db.connect()
    output = {
        OutputObjType.fns: get_fns,
        OutputObjType.views: get_views,
    }[args.objtype](args)
    print(output)
    return


if __name__ == '__main__':
    main()
