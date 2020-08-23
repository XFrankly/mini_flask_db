import weakref
import gc
from pprint import pprint


class Graph(object):
    def __init__(self, name):
        self.name = name
        self.other = None

    def set_next(self, other):
        """

        Args:
            other:

        Returns:

        """
        print(f"{self.name}.set_next({other})")

    def all_nodes(self):
        yield self
        n = self.other
        while n and n.name != self.name:
            yield n
            n = n.other
        if n is self:
            yield n
        return

    def __str__(self):
        return "->".join(n.name for n in self.all_nodes())

    def __repr__(self):
        return f"<{self.__class__.__name__} at 0x{id(self)} name={self.name}>"

    def __del__(self):
        print(f"(Deleting {self.name})")

class WeakGraph(Graph):
    def set_next(self, other):
        if other is not None:
            if self in other.all_nodes():
                other = weakref.proxy(other)
        super(WeakGraph, self).set_next(other)
        return


def collect_and_show_garbage():
    print(f"Collecting...")
    n = gc.collect()
    print(f"unreachable objects:{n}")
    print(f"garbage:",)
    pprint(gc.garbage)

def demo(graph_factory):
    print("Set up graph:")
    one = graph_factory("one")
    two = graph_factory("two")
    three = graph_factory("three")
    one.set_next(two)
    two.set_next(three)
    three.set_next(one)

    print()
    print(f"Graph:")
    print(str(one))
    collect_and_show_garbage()

    print()
    three = None
    two = None
    print("After 2 references removed")
    print(str(one))
    collect_and_show_garbage()

    print()
    print("removeing last reference")
    one = None
    collect_and_show_garbage()


if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_LEAK)
    print(f"Setting up the cycle")
    print()
    demo(Graph)
    demo(WeakGraph)
    print()
    print("breaking the cycle and cleaning up garbage")
    print(gc.garbage)
    gc.garbage[0].set_next(None)
    while gc.garbage:
        del gc.garbage[0]
    print()
    collect_and_show_garbage()

    demo(WeakGraph)

