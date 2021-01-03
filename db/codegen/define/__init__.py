from typing import List

from typez import DefineLang, FnRecord, TableRecord
from . import scala_define
from . import python_define


def _get_def_module(lang: DefineLang):
    return {
        DefineLang.scala: scala_define,
        DefineLang.python: python_define,
    }[lang]


def get_fn_def_file_contents(schema: str, lang: DefineLang, fns: List[FnRecord]) -> str:
    def_module = _get_def_module(lang)
    impl_language_defs = [
        def_module.get_impl_language_fn_def(schema, fn) for fn in fns]
    fn_defs = "\n".join(impl_language_defs)
    return def_module.wrap_fn_defs(fn_defs)


def get_view_def_file_contents(schema: str, lang: DefineLang, views: List[TableRecord]) -> str:
    def_module = _get_def_module(lang)
    impl_language_defs = [
        def_module.get_impl_language_model_def(schema, view)
        for view in views]
    defs = "\n\n".join(impl_language_defs)
    return def_module.wrap_view_defs(defs)
