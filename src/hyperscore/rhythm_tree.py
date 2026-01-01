import copy
from dataclasses import dataclass
from pathlib import Path

from lark import Lark, Transformer


@dataclass(frozen=True)
class RhythmTree:
    nodes: list

    def expand(self, ms: int) -> list[int]:
        ms_sum = ms
        value_sum = 0
        for n in self.nodes:
            value_sum += n.value

        ret = []
        for i in range(len(self.nodes) - 1):
            node = self.nodes[i]
            assignment = int(ms * node.value / value_sum)
            ret.extend(node.expand(assignment))
            ms_sum -= assignment

        node = self.nodes[-1]
        assignment = ms_sum
        ret.extend(node.expand(assignment))

        return ret


@dataclass(frozen=True)
class Atom:
    value: int

    def expand(self, ms: int) -> list[int]:
        return [ms]


@dataclass(frozen=True)
class Children:
    value: int
    nodes: RhythmTree

    def expand(self, ms: int) -> list[int]:
        return self.nodes.expand(ms)


@dataclass(frozen=True)
class Division:
    value: int
    denominator: int

    def expand(self, ms: int) -> list[int]:
        unit = int(ms / self.denominator)

        ret = []
        for i in range(self.denominator - 1):
            ret.append(unit)

        ret.append(ms - unit * (self.denominator - 1))

        return ret


class RhythmTreeTransformer(Transformer):
    def start(self, tree: list):
        ret = []
        for t in tree:
            if isinstance(t, list):
                ret.extend(t)
            else:
                ret.append(t)
        return RhythmTree(ret)

    def repeat(self, tree: list):
        ret = []
        for i in range(int(tree[1])):
            ret.append(copy.deepcopy(tree[0]))
        return ret

    def atom(self, tree: list):
        return Atom(int(tree[0]))

    def children(self, tree: list):
        return Children(int(tree[0]), tree[1])

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
