from __future__ import annotations

from collections.abc import Sequence as Seq
from dataclasses import dataclass
from fractions import Fraction

from lark import Lark, Token, Transformer, v_args

from hyperscore.core.time import TimeSpan

# ============================================================
# Grammar
# ============================================================

GRAMMAR = r"""
start: sequence

sequence: expr+                       -> sequence

?expr: primary postfix*               -> apply_postfix

postfix: "*" INT                      -> repeat_op
       | "%" INT                      -> split_op

?primary: group
        | atom
        | "(" sequence ")"            -> parens

group: atom "[" sequence "]"          -> group

atom: INT "/" INT                     -> fraction
    | INT                             -> integer

%import common.INT
%import common.WS
%ignore WS
"""

# ============================================================
# AST Nodes
# ============================================================


@dataclass(frozen=True)
class Atom:
    value: Fraction


@dataclass(frozen=True)
class Group:
    weight: Atom
    body: Sequence


@dataclass(frozen=True)
class Repeat:
    node: Node
    times: int


@dataclass(frozen=True)
class Split:
    node: Node
    parts: int


@dataclass(frozen=True)
class Sequence:
    items: list[Node]


Node = Atom | Group | Repeat | Split | Sequence

# ============================================================
# Parser
# ============================================================


@v_args(inline=True)
class RhythmTransformer(Transformer):
    def INT(self, tok: Token) -> int:
        return int(tok)

    def start(self, seq: Sequence):
        return seq

    def sequence(self, *items: Node):
        return Sequence(list(items))

    def parens(self, seq: Sequence):
        return seq

    def integer(self, value: int):
        return Atom(Fraction(value, 1))

    def fraction(self, num: int, den: int):
        return Atom(Fraction(num, den))

    def group(self, weight: Atom, body: Sequence):
        return Group(weight=weight, body=body)

    def repeat_op(self, times: int):
        return ("repeat", times)

    def split_op(self, parts: int):
        return ("split", parts)

    def apply_postfix(self, base: Node, *ops):
        node = base
        for kind, n in ops:
            if kind == "repeat":
                node = Repeat(node=node, times=n)
            elif kind == "split":
                node = Split(node=node, parts=n)
            else:
                raise ValueError(kind)
        return node


def parse_rhythm(text: str) -> Sequence:
    """
    Parse rhythm DSL into raw AST (may include Repeat / Split).
    """
    parser = Lark(GRAMMAR, parser="lalr", transformer=RhythmTransformer())
    ast = parser.parse(text)
    assert isinstance(ast, Sequence)
    return ast


# ============================================================
# Normalization
# ============================================================


def normalize(node: Node) -> Node:
    """
    Normalize rhythm AST.

    Eliminates:
      - Repeat
      - Split

    Result invariant:
      - AST contains only Atom / Group / Sequence
      - Sequence.items NEVER contains nested Sequence
    """
    if isinstance(node, Atom):
        return node

    if isinstance(node, Group):
        return Group(
            weight=node.weight,
            body=_normalize_sequence(node.body),
        )

    if isinstance(node, Sequence):
        return _normalize_sequence(node)

    if isinstance(node, Split):
        base = normalize(node.node)
        if not isinstance(base, Atom):
            raise TypeError("Split base must normalize to Atom")

        ones = [Atom(Fraction(1, 1)) for _ in range(node.parts)]
        return Group(
            weight=base,
            body=Sequence(ones),
        )

    if isinstance(node, Repeat):
        base = normalize(node.node)

        items: list[Node] = []
        for _ in range(node.times):
            if isinstance(base, Sequence):
                # flatten
                items.extend(base.items)
            else:
                items.append(base)

        return Sequence(items)

    raise TypeError(node)


def _normalize_sequence(seq: Sequence) -> Sequence:
    items: list[Node] = []

    for item in seq.items:
        n = normalize(item)
        if isinstance(n, Sequence):
            # flatten nested sequence
            items.extend(n.items)
        else:
            items.append(n)

    return Sequence(items)


# ============================================================
# Fraction expansion
# ============================================================


def node_weight(node: Node) -> Fraction:
    """
    Weight of a node relative to its parent.
    Assumes normalized AST.
    """
    if isinstance(node, Atom):
        return node.value

    if isinstance(node, Group):
        return node.weight.value

    if isinstance(node, Sequence):
        total = sum(node_weight(child) for child in node.items)
        if total == 0:
            raise ValueError("Sequence weight must be non-zero")
        return total

    raise TypeError(node)


def expand_sequence(seq: Sequence) -> list[Fraction]:
    """
    Expand normalized Sequence into relative duration fractions.
    Sum of result == 1.
    """
    weights = [node_weight(n) for n in seq.items]
    total = sum(weights)

    if total == 0:
        raise ValueError("Total weight must be non-zero")

    out: list[Fraction] = []

    for node, w in zip(seq.items, weights):
        share = w / total

        if isinstance(node, Atom):
            out.append(share)

        elif isinstance(node, Group):
            inner = expand_sequence(node.body)
            out.extend(share * d for d in inner)

        else:
            # normalized invariant should prevent this
            raise TypeError(f"Unexpected node: {node!r}")

    return out


def expand_to_fractions(ast: Sequence) -> list[Fraction]:
    """
    High-level API:
    normalized Sequence → duration fractions (sum == 1)
    """
    durations = expand_sequence(ast)
    if sum(durations) != Fraction(1, 1):
        raise AssertionError("Duration sum is not 1")
    return durations


# ============================================================
# Quantization (Largest Remainder Method)
# ============================================================


def quantize_fractions(
    durations: Seq[Fraction],
    *,
    total: int,
) -> list[int]:
    """
    Quantize duration fractions into integer ticks using
    Largest Remainder Method.

    Guarantees:
      - sum(result) == total
    """
    if total <= 0:
        raise ValueError("total must be positive")

    if sum(durations) != Fraction(1, 1):
        raise ValueError("durations must sum to 1")

    ideal = [d * total for d in durations]
    base = [int(x) for x in ideal]

    remaining = total - sum(base)
    if remaining < 0:
        raise AssertionError("Negative remaining")

    remainders = sorted(
        range(len(ideal)),
        key=lambda i: ideal[i] - base[i],
        reverse=True,
    )

    for i in range(remaining):
        base[remainders[i]] += 1

    return base


# ============================================================
# TimeSpan API (public)
# ============================================================


def rhythm_ast_to_timespans(
    ast: Sequence,
    *,
    total: int,
    start: int = 0,
) -> list[TimeSpan]:
    """
    High-level API:

        rhythm DSL
          → AST
          → normalized AST
          → duration fractions
          → quantized ticks
          → TimeSpan sequence
    """
    norm = normalize(ast)
    assert isinstance(norm, Sequence)

    fractions = expand_to_fractions(norm)
    ticks = quantize_fractions(fractions, total=total)

    t = start
    spans: list[TimeSpan] = []
    for d in ticks:
        spans.append(TimeSpan(start=t, duration=d))
        t += d

    return spans
