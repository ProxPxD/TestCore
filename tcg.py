import warnings
from collections.abc import Iterable, Sequence
from typing import Any, Optional

import pytest
from _pytest.mark import Mark, ParameterSet
from _pytest.mark.structures import MarkDecorator
from pydash import chain as c
from toolz import unique

from .utils import apply

warnings.filterwarnings('ignore', category=pytest.PytestUnknownMarkWarning)


class TCG:
    """
    TCG - Test Case Generator
    """
    tcs: Optional[Sequence[Any]] = None

    @classmethod
    def generate_tcs(cls) -> list[Any]:
        return list(cls.tcs if cls.tcs is not None else [])

    @classmethod
    def map(cls, tc: Any) -> Any:
        return tc

    @classmethod
    def map_to_many(cls, tc: Any) -> Iterable[Any]:
        return [tc]

    @classmethod
    def gather_tag_before_mapping_to_many(cls, tc: Any) -> Iterable[str]:  # noqa: ARG003
        return []

    @classmethod
    def gather_tags(cls, tc: Any) -> Iterable[str]:
        return getattr(tc, 'tags', [])

    @classmethod
    def param_names(cls) -> Sequence[str] | str:
        raise ValueError()  # TODO: replace exception

    ###############
    # Undefinable #
    ###############

    @classmethod
    def _generate_marks(cls, tags: Iterable[str]) -> list[Mark]:
        return [cls._create_mark(tag) for tag in tags]

    @classmethod
    def _create_mark(cls, tag: str) -> Mark:
        name, *subs = tag.split('/')
        base_mark_decorator: MarkDecorator = pytest.mark.__getattr__(name.replace('-', '_'))
        return base_mark_decorator(*subs).mark

    @classmethod
    def _as_paramset(cls, tc: Any, tags: Iterable[str] = None) -> ParameterSet:
        marks: list[Mark] = cls._generate_marks(tags or [])
        tc = cls.map(tc)
        values: tuple[Any, ...] = (tc, ) if hasattr(tc, '_asdict') or not isinstance(tc, tuple) else tc
        return pytest.param(*values, marks=marks)

    @classmethod
    @apply(list)
    def generate_params(cls) -> Iterable[ParameterSet]:
        for big_tc in cls.generate_tcs():
            big_tags: list[str] = list(cls.gather_tag_before_mapping_to_many(big_tc))
            for lil_tc in cls.map_to_many(big_tc):
                lil_tags: list[str] = list(cls.gather_tags(lil_tc))
                yield cls._as_paramset(lil_tc, unique(big_tags + lil_tags))

    @classmethod
    def create_name(cls, tc: Any) -> Optional[str]:  # noqa: ARG003
        return None

    @classmethod
    def parametrize(cls,
            param_names: str | Sequence[str]=None,
            name_from: str | int | Sequence[str|int] = None,
            ids: Any = None,
            **kwargs: Any,
        ) -> MarkDecorator:
        def get_tag_brackets(tc: Any) -> str:
            return ' - (' + ', '.join(getattr(tc, 'tags', '')) + ') '
        if ids is None:
            name_from: Sequence[str | int] = (name_from, ) if isinstance(name_from, (str | int)) else name_from or ('name', 'short', 'descr')
            ids = lambda tc: cls.create_name(tc) or (c().at(*name_from).filter(bool).concat(tc).head()(tc) + get_tag_brackets(tc))  # noqa: E731
        param_names = param_names or cls.param_names()
        params = cls.generate_params()
        return pytest.mark.parametrize(param_names, params, ids=ids, **kwargs)
