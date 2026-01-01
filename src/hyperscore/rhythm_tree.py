import copy
from dataclasses import dataclass
from pathlib import Path

from lark import Lark, Transformer


@dataclass(frozen=True)
class RhythmNode:
    weight: float

    def expand(self, ms: int) -> list[int]:
        raise NotImplementedError


@dataclass(frozen=True)
class Atom(RhythmNode):
    def expand(self, ms: int) -> list[int]:
        return [ms]


@dataclass(frozen=True)
class Division(RhythmNode):
    denominator: int

    def expand(self, ms: int) -> list[int]:
        unit = int(ms / self.denominator)
        ret = [unit] * (self.denominator - 1)
        ret.append(ms - unit * (self.denominator - 1))
        return ret


@dataclass(frozen=True)
class RhythmTree(RhythmNode):
    children: list[RhythmNode]

    def expand(self, ms: int) -> list[int]:
        # TODO: use largest remainder method and fraction

        ms_tmp = ms
        weight_sum = sum([n.weight for n in self.children])

        ret = []
        for n in self.children[:-1]:
            assign_ms = int(ms * n.weight / weight_sum)
            ret.extend(n.expand(assign_ms))
            ms_tmp -= assign_ms

        ret.extend(self.children[-1].expand(ms_tmp))
        return ret


class RhythmTreeTransformer(Transformer):
    def start(self, tree: list):
        ret = []
        for t in tree:
            if isinstance(t, list):
                ret.extend(t)
            else:
                ret.append(t)
        return RhythmTree(1, ret)

    def repeat(self, tree: list):
        ret = []
        for i in range(int(tree[1])):
            ret.append(copy.deepcopy(tree[0]))
        return ret

    def atom(self, tree: list):
        return Atom(int(tree[0]))

    def children(self, tree: list):
        return RhythmTree(int(tree[0]), tree[1])

    def division(self, tree: list):
        return Division(int(tree[0]), int(tree[1]))


class RhythmTreeParser:
    def __init__(self):
        grammer_file = Path(__file__).resolve().parent.joinpath("rhythm_tree_grammer.lark")
        with Path.open(grammer_file) as f:
            self._parser = Lark(f)
        self._transformer = RhythmTreeTransformer()

    def parse(self, expr: str) -> RhythmTree:
        tree = self._parser.parse(expr)
        return self._transformer.transform(tree)


if __name__ == "__main__":
    p = RhythmTreeParser()
    x = p.parse("1*2 1[2 3]*2 1/3*2")
    print(x)

    y = p.parse("5 4 2 4 5")
    print(y)
    print(y.expand(1000))
