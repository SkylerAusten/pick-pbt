from __future__ import annotations

from collections import defaultdict, deque


def topsort_implementation(edges: list[tuple[str, str]]) -> list[str]:
    """Topological sort for a DAG represented as a list of directed edges.

    Args:
        edges: A list of (u, v) tuples representing directed edges.

    Returns:
        A list of vertices in a topological order.

    Notes:
        This implementation assumes the input graph is a DAG.
    """
    # Build graph and in-degrees
    adj: defaultdict[str, list[str]] = defaultdict(list)
    in_degree: defaultdict[str, int] = defaultdict(int)
    nodes: set[str] = set()

    for u, v in edges:
        adj[u].append(v)
        nodes.add(u)
        nodes.add(v)
        in_degree[v] += 1
        if u not in in_degree:
            in_degree[u] = 0

    # L = empty list to store ordering
    ordering: list[str] = []

    # S = set of vertices with no incoming edges
    sources = sorted([n for n in nodes if in_degree[n] == 0])
    queue: deque[str] = deque(sources)

    while queue:
        u = queue.popleft()
        ordering.append(u)

        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    return ordering
