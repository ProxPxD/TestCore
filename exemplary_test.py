from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field, replace

from testing.core import TCG


def exemplary_logic(string: str) -> str:
    return ' '.join(string.upper())


@dataclass
class TC:
    descr: str

    input: str | list[str]
    expected: str | list[str]

    tags: set[str] = field(default_factory=set)


@dataclass
class Tc:
    descr: str

    input: str
    expected: str

    tags: set[str] = field(default_factory=set)


class ExemplaryTCG(TCG):
    tcs = [
        TC('Trivial - already upper case', input='X', expected='X', tags={'upper'}),
        TC('Simple', input='h', expected='H'),
        TC('Double test for tags passing', input=['lol', 'lmao'], expected=['L O L', 'L M A O']),
    ]

    @classmethod
    def generate_tcs(cls) -> list:
        tcs = list(cls.tcs)
        tcs.extend([
            TC('Test that needs functional operations', input='kidding', expected='K I D D I N G'),
        ])
        return tcs

    @classmethod
    def premap(cls, tc: TC) -> TC:
        tc.input = [tc.input] if isinstance(tc.input, str) else tc.input
        tc.expected = [tc.expected] if isinstance(tc.expected, str) else tc.expected
        if len(tc.input) != len(tc.expected):
            raise ValueError('TC should have the same number of inputs and expected')
        return tc

    @classmethod
    def map_to_many(cls, tc: TC) -> Iterable[Tc]:
        for i, e in zip(tc.input, tc.expected, strict=True):
            yield Tc(**asdict(replace(tc, input=i, expected=e)))

    @classmethod
    def gather_tags(cls, tc: Tc) -> Iterable[str]:
        if 'functional' in tc.descr:
            tc.tags.add('functional')
        return tc.tags

    @classmethod
    def create_name(cls, tc) -> str | None:
        return f'{tc.descr}: "{tc.input}", ({", ".join(tc.tags)})'


@ExemplaryTCG.parametrize('tc')
def test(tc: Tc):
    actual = exemplary_logic(tc.input)
    assert actual == tc.expected
