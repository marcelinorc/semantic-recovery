from pygraph.classes.digraph import digraph


def dominator_tree_dfs(graph, node, visited, index=0):
    """
    Makes the lengauer tarjan dominator tree algorithm Deep First Search
    """
    result = [node]
    node.dom_idx = index
    node.predecessors = graph.incidents(node)
    node.successors = graph.neighbors(node)
    visited.append(node)
    for n in node.successors:
        if n not in visited:
            n.dom_parent = node
            result.extend(dominator_tree_dfs(graph, n, visited, index + 1))

    return result


def build_dominator_tree(graph, root):
    """
    Builds the Lengauer Tarjan dominator tree algorithm
    """
    # Initialization
    vertex = dominator_tree_dfs(graph, root, [])

    for i in range(len(vertex) - 1, 0, -1):
        w = vertex[i]
        p = w.dom_parent
        for v in w.predecessors:
            u = dominator_eval(v)
            if u.dom_semi_idx < w.dom_semi_idx:
                w.dom_semi = u.dom_semi

        # vertex[w.dom_semi_idx].dom_bucket.append(w)
        w.dom_semi.dom_bucket.append(w)
        # LINK:
        w.dom_ancestor = p

        while len(p.dom_bucket) > 0:
            v = p.dom_bucket.pop()
            u = dominator_eval(v)
            v.idom = u if u.dom_semi_idx < v.dom_semi_idx else w.dom_parent

    for i in range(1, len(vertex)):
        w = vertex[i]
        if w.idom != w.dom_semi:
            w.idom = w.idom.idom

    vertex[0].idom = None

    graph._has_computed_dominators = True

    tree = digraph()
    for n in graph:
        tree.add_node(n)
    for n in graph:
        if n.idom is not None:
            if not n in n.idom.dom_successors:
                n.idom.dom_successors.append(n)
            if not tree.has_edge((n.idom, n)):
                tree.add_edge((n.idom, n))
    return tree


def dominator_eval(v):
    """
    Lengauer Tarjan dominator tree algorithm simple eval function
    """
    a = v.dom_ancestor
    if a is None:
        return v
    while a.dom_ancestor is not None:
        if v.dom_semi_idx > a.dom_semi_idx:
            v = a
        a = a.dom_ancestor
    return v