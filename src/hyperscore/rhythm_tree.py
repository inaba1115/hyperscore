from __future__ import annotations

from dataclasses import dataclass

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
    """Repeat を展開し、Sequence を平坦化する正規化。"""
    if isinstance(node, (Atom, Division)):
        return node

    if isinstance(node, Group):
        return Group(node.weight, normalize_sequence(node.body))

    if isinstance(node, Repeat):
        # Repeat(node, n) を Sequence に展開
        expanded = [normalize(node.node) for _ in range(node.n)]
        return Sequence(expanded)

    if isinstance(node, Sequence):
        return normalize_sequence(node)

    raise TypeError(f"Unknown node: {node!r}")


def normalize_sequence(seq: Sequence) -> Sequence:
    out: list[Node] = []
    for item in seq.items:
        item_n = normalize(item)
        # Sequence の入れ子を平坦化
        if isinstance(item_n, Sequence):
            out.extend(item_n.items)
        else:
            out.append(item_n)
    return Sequence(out)


if __name__ == "__main__":
    # ast = parse_rhythm("3 [ (1/2)*3 2 ] 5")
    ast = parse_rhythm("3[1 2 3] 1")
    print(ast)

    norm = normalize(ast)
    print(norm)
