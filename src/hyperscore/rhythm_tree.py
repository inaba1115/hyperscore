from __future__ import annotations

from collections.abc import Sequence as Seq
from dataclasses import dataclass
from fractions import Fraction

from lark import Lark, Token, Transformer, v_args

GRAMMAR = r"""
start: sequence

sequence: element+

?element: repeated
        | simple

repeated: simple "*" INT
        | "(" simple ")" "*" INT -> repeat
        

?simple: atom
       | group
       | division

atom: INT                     -> atom
group: INT "[" sequence "]"   -> group
division: INT "/" INT         -> division

%import common.INT
%import common.WS
%ignore WS
"""


@dataclass(frozen=True)
class Atom:
    value: int


@dataclass(frozen=True)
class Division:
    num: int
    den: int


@dataclass(frozen=True)
class Group:
    weight: int
    body: Sequence


@dataclass(frozen=True)
class Repeat:
    node: Node
    n: int


@dataclass(frozen=True)
class Sequence:
    items: list[Node]


Node = Atom | Division | Group | Repeat | Sequence


@v_args(inline=True)
class RhythmTransformer(Transformer):
    def INT(self, tok: Token) -> int:
        return int(tok)

    def start(self, items):
        return items

    def sequence(self, *items):
        return Sequence(list(items))

    def atom(self, value: int):
        return Atom(value)

    def division(self, num: int, den: int):
        return Division(num, den)

    def group(self, weight: int, body: Sequence):
        return Group(weight, body)

    def repeat(self, node: Node, n: int):
        return Repeat(node, n)


def parse_rhythm(text: str) -> Sequence:
    parser = Lark(GRAMMAR, parser="lalr", transformer=RhythmTransformer())
    return parser.parse(text)  # type: ignore


def normalize(node: Node) -> Node:
    if isinstance(node, (Atom, Division)):
        return node

    if isinstance(node, Group):
        return Group(node.weight, normalize_sequence(node.body))

    if isinstance(node, Repeat):
        expanded = [normalize(node.node) for _ in range(node.n)]
        return Sequence(expanded)

    if isinstance(node, Sequence):
        return normalize_sequence(node)

    raise TypeError(f"Unknown node: {node!r}")


def normalize_sequence(seq: Sequence) -> Sequence:
    out: list[Node] = []
    for item in seq.items:
        item_n = normalize(item)
        if isinstance(item_n, Sequence):
            out.extend(item_n.items)
        else:
            out.append(item_n)
    return Sequence(out)


def node_weight(node: Node) -> Fraction:
    if isinstance(node, Atom):
        return Fraction(node.value, 1)

    if isinstance(node, Division):
        return Fraction(node.num, node.den)

    if isinstance(node, Group):
        # Group 自身の weight は「外側に対する比率」
        return Fraction(node.weight, 1)

    raise TypeError(node)


def expand_sequence(seq: Sequence) -> list[Fraction]:
    weights = [node_weight(n) for n in seq.items]
    total = sum(weights)

    out: list[Fraction] = []

    for node, w in zip(seq.items, weights):
        share = w / total

        if isinstance(node, Group):
            # Group 内部は再帰的に分割
            inner = expand_sequence(node.body)
            out.extend([share * d for d in inner])
        else:
            out.append(share)

    return out


def quantize_durations_to_ticks(
    durations: Seq[Fraction],
    total_ticks: int,
) -> list[int]:
    ideal = [d * total_ticks for d in durations]
    base = [int(x) for x in ideal]

    remaining = total_ticks - sum(base)

    remainders = sorted(
        enumerate([i - b for i, b in zip(ideal, base)]),
        key=lambda x: x[1],
        reverse=True,
    )

    for i in range(remaining):
        idx, _ = remainders[i]
        base[idx] += 1

    return base


def rhythm_to_ticks(
    ast: Sequence,
    *,
    total_ticks: int,
) -> list[int]:
    norm = normalize(ast)
    assert isinstance(norm, Sequence)

    durations_frac = expand_sequence(norm)
    return quantize_durations_to_ticks(durations_frac, total_ticks)


if __name__ == "__main__":
    ast = parse_rhythm("3 [ (1/2)*3 2 ] 3")
    ticks = rhythm_to_ticks(ast, total_ticks=1000)
    print(ticks)
    print(sum(ticks))
