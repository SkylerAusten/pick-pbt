import unittest

from toposort.toposort import topsort_implementation


def _is_valid_toposort(edges: list[tuple[str, str]], order: list[str]) -> bool:
    nodes = {u for u, _ in edges} | {v for _, v in edges}
    if nodes and (set(order) != nodes or len(order) != len(nodes)):
        return False
    if not nodes and order != []:
        return False

    pos = {node: i for i, node in enumerate(order)}
    for u, v in edges:
        if pos[u] > pos[v]:
            return False
    return True


class TestToposortImplementation(unittest.TestCase):
    def test_empty_graph(self) -> None:
        self.assertEqual(topsort_implementation([]), [])

    def test_single_edge(self) -> None:
        edges = [("A", "B")]
        order = topsort_implementation(edges)
        self.assertEqual(order, ["A", "B"])  # deterministic for this input
        self.assertTrue(_is_valid_toposort(edges, order))

    def test_diamond_graph(self) -> None:
        # A must come before B and C; both before D.
        edges = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
        order = topsort_implementation(edges)
        self.assertEqual(order, ["A", "B", "C", "D"])  # deterministic given edge order
        self.assertTrue(_is_valid_toposort(edges, order))

    def test_disconnected_components(self) -> None:
        edges = [("A", "B"), ("C", "D")]
        order = topsort_implementation(edges)
        self.assertEqual(order, ["A", "C", "B", "D"])  # deterministic given algorithm+sorting
        self.assertTrue(_is_valid_toposort(edges, order))

    def test_multiple_sources_single_sink(self) -> None:
        edges = [("A", "D"), ("B", "D"), ("C", "D")]
        order = topsort_implementation(edges)
        self.assertTrue(_is_valid_toposort(edges, order))
        self.assertEqual(order[-1], "D")


if __name__ == "__main__":
    unittest.main()
