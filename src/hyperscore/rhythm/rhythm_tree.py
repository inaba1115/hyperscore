from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from lark import Lark, Token, Transformer, v_args

from hyperscore.core.time import TimeSpan

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

# ---------- AST Nodes ----------


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


@v_args(inline=True)
class RhythmTransformer(Transformer):
    # ----------- terminals -----------

    def INT(self, tok: Token) -> int:
        return int(tok)

    # ----------- structure -----------

    def start(self, seq: Sequence):
        return seq

    def sequence(self, *items: Node):
        return Sequence(list(items))

    def parens(self, seq: Sequence):
        return seq

    # ----------- atom -----------

    def integer(self, value: int):
        return Atom(Fraction(value, 1))

    def fraction(self, num: int, den: int):
        return Atom(Fraction(num, den))

    # ----------- group -----------

    def group(self, weight: Atom, body: Sequence):
        return Group(weight=weight, body=body)

    # ----------- postfix ops -----------

    def repeat_op(self, times: int):
        return ("repeat", times)

    def split_op(self, parts: int):
        return ("split", parts)

    # ----------- postfix application -----------

    def apply_postfix(self, base: Node, *ops):
        node = base
        for op in ops:
            kind, n = op
            if kind == "repeat":
                node = Repeat(node=node, times=n)
            elif kind == "split":
                node = Split(node=node, parts=n)
            else:
                raise ValueError(op)
        return node


def parse_rhythm(text: str) -> Sequence:
    parser = Lark(
        GRAMMAR,
        parser="lalr",
        transformer=RhythmTransformer(),
    )

    ast = parser.parse(text)
    assert isinstance(ast, Sequence)

    return ast


def normalize(node: Node) -> Node:
    """
    Split / Repeat を消去し、
    Atom / Group / Sequence のみからなる正規形 AST を返す
    """
    if isinstance(node, Atom):
        return node

    if isinstance(node, Sequence):
        return _normalize_sequence(node)

    if isinstance(node, Group):
        return Group(
            weight=node.weight,
            body=_normalize_sequence(node.body),
        )

    if isinstance(node, Split):
        # x % n  →  x[1 1 ... 1]
        base = normalize(node.node)
        if not isinstance(base, Atom):
            raise TypeError("Split base must normalize to Atom")
        ones = [Atom(Fraction(1, 1)) for _ in range(node.parts)]
        return Group(
            weight=base,
            body=Sequence(ones),
        )

    if isinstance(node, Repeat):
        # x * n  →  x x ... x
        base = normalize(node.node)
        return Sequence([base for _ in range(node.times)])

    raise TypeError(f"Unknown node: {node!r}")


def _normalize_sequence(seq: Sequence) -> Sequence:
    items: list[Node] = []
    for item in seq.items:
        n = normalize(item)

        # Repeat の結果などで Sequence が入れ子になるので平坦化
        if isinstance(n, Sequence):
            items.extend(n.items)
        else:
            items.append(n)

    return Sequence(items)


def node_weight(node) -> Fraction:
    """
    ノードの「外側に対する重み」を返す。
    正規化後 AST(Atom / Group / Sequence のみ)を想定。
    """
    if isinstance(node, Atom):
        return node.value

    if isinstance(node, Group):
        return node.weight.value

    if isinstance(node, Sequence):
        # Sequence の重み = 子ノードの重みの総和
        total = sum(node_weight(child) for child in node.items)
        if total == 0:
            raise ValueError("Sequence weight must be non-zero")
        return total

    raise TypeError(f"Unsupported node type: {node!r}")


def expand_sequence(seq: Sequence) -> list[Fraction]:
    """
    Sequence を相対 duration(Fraction, 合計=1)に展開する
    """
    # 各要素の外側重み
    weights = [node_weight(n) for n in seq.items]
    total = sum(weights)

    if total == 0:
        raise ValueError("Total weight must be non-zero")

    durations: list[Fraction] = []

    for node, w in zip(seq.items, weights):
        share = w / total  # このノードに割り当てられる全体比率

        if isinstance(node, Atom):
            # 葉: そのまま 1 音分
            durations.append(share)

        elif isinstance(node, Group):
            # 再帰的に内部を分割
            inner = expand_sequence(node.body)
            durations.extend([share * d for d in inner])

        elif isinstance(node, Sequence):
            inner = expand_sequence(node)
            durations.extend([share * d for d in inner])

        else:
            raise TypeError(f"Unexpected node type: {node!r}")

    return durations


def expand_to_fractions(ast: Sequence) -> list[Fraction]:
    """
    正規化済み AST(Sequence)から
    Fraction duration 列(合計=1)を生成
    """
    durations = expand_sequence(ast)

    # 安全チェック(デバッグ用)
    if sum(durations) != Fraction(1, 1):
        raise AssertionError("Duration sum is not 1")

    return durations


def quantize_fractions_to_ticks(
    durations: Sequence[Fraction],
    total_ticks: int,
) -> list[int]:
    """
    Fraction duration 列(合計=1)を tick(ms) に量子化する。
    - 合計 tick は必ず total_ticks
    - largest remainder method 使用
    """
    if total_ticks <= 0:
        raise ValueError("total_ticks must be positive")

    if sum(durations) != Fraction(1, 1):
        raise ValueError("durations must sum to 1")

    # 理想 tick(Fraction)
    ideal = [d * total_ticks for d in durations]

    # 切り捨て(floor)
    base = [int(x) for x in ideal]

    # 残り tick
    remaining = total_ticks - sum(base)
    if remaining < 0:
        raise AssertionError("Negative remaining ticks")

    # 小数部(剰余)を計算
    remainders = [(i, ideal[i] - base[i]) for i in range(len(ideal))]

    # 剰余が大きい順に +1 を配分
    remainders.sort(key=lambda x: x[1], reverse=True)

    for k in range(remaining):
        idx, _ = remainders[k]
        base[idx] += 1

    return base


def durations_to_start_ticks(durations_tick: Sequence[int]) -> list[int]:
    """
    duration tick 列から start_tick 列を生成
    """
    t = 0
    starts = []
    for d in durations_tick:
        starts.append(t)
        t += d
    return starts


def rhythm_ast_to_ticks(
    ast: Sequence,
    *,
    total_ticks: int,
) -> list[int]:
    norm = normalize(ast)
    assert isinstance(norm, Sequence)

    durations_frac = expand_to_fractions(norm)
    return quantize_fractions_to_ticks(durations_frac, total_ticks)


def durations_to_timespans(
    durations: list[int],
    *,
    start: int = 0,
) -> list[TimeSpan]:
    t = start
    spans = []
    for d in durations:
        spans.append(TimeSpan(t, d))
        t += d
    return spans
