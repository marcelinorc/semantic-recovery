from pygraph.classes.digraph import digraph
from metadata.static_analysis.dominators import build_dominator_tree


def build_dominance_frontier(graph):
    """
    Finds the dominance frontiers for an smart phi function placement in the SSA form.

    It assumes that the CFGBlocks have already their dominators computed
    """
    if not graph.has_computed_dominators:
        raise RuntimeError("Cannot compute dominance frontier in a graph without computed dominators")

    for n in graph:
        if len(n.predecessors) > 0:
            for p in n.predecessors:
                runner = p
                while runner != n.idom:
                    if n not in runner.dom_frontier:
                        runner.dom_frontier.append(n)
                    runner = runner.idom

    graph._has_computed_dominance_frontier = True


def place_phi_nodes(graph):
    """
    Find those variables that are used in more than one block
    """
    if not graph.has_computed_dominators:
        raise RuntimeError("Cannot compute dominance PHI functions without dominance frontiers")

    blocks = {}
    globals_vars = []
    for node in graph:
        var_kill = []
        for inst in node.instructions:
            read = inst.registers_read()
            written = inst.registers_written()

            for r in read:
                if r not in globals_vars and r not in var_kill:
                    globals_vars.append(r)
            for w in written:
                if w not in var_kill:
                    var_kill.append(w)
                if w in blocks:
                    if node not in blocks[w]:
                        blocks[w].append(node)
                else:
                    blocks[w] = [node]

    # place the nodes
    for x in globals_vars:
        if x in blocks:
            work_list = blocks[x]
            i = 0
            while i < len(work_list):
                b = work_list[i]
                for d in b.dom_frontier:
                    j, k = 0, list(d.phi_functions.keys())
                    while j < len(d.phi_functions) and k[j][0] != x:
                        j += 1
                    if i >= len(d.phi_functions):
                        d.phi_functions[(x, 0)] = []
                        if d not in work_list:
                            work_list.append(d)
                i += 1

    return globals_vars


class SSAFormBuilder(object):
    """
    Computes the ssa form of a ARM instructions
    """

    def __init__(self, instructions, graph, root):
        self._graph = graph
        self._root = root
        self._instructions = instructions

    def build(self):
        # Compute the Dominators tree
        build_dominator_tree(self._graph, self._root)
        # Compute dominance frontiers
        build_dominance_frontier(self._graph)
        # Find global names tpo minimize phi function emplacement
        global_vars = place_phi_nodes(self._graph)

        self._rename_vars(global_vars)

        d = digraph()
        for inst in self._instructions:
            for r in inst.ssa_written:
                if r not in d:
                    d.add_node(r)
                for w in inst.ssa_read:
                    if w not in d:
                        d.add_node(w)
                    if not d.has_edge((r, w)):
                        d.add_edge((r, w))
        return d

    def _place_phi_nodes(self):
        pass

    @staticmethod
    def _new_name(n, counter, stack):
        """
        Increases the counter for a given variable and returns a tuple containing the variable name and ssa index
        """
        k = n if type(n) is int else n[0]
        i = counter[k]
        stack[k].insert(0, i)
        counter[k] += 1
        return k, i

    def _rename_vars(self, global_vars):
        """
        Rename the variables in the SSA
        """
        counter = {}
        stack = {}
        for v in range(0, 16):
            counter[v] = 0
            stack[v] = [0]

        self._rename_node(self._root, counter, stack)

    def _rename_node(self, n, counter, stack):
        """
        Rename the variables in SSA form in the nodes of the CFG
        """
        keys = []
        keys.extend(n.phi_functions.keys())
        for phi in keys:
            # Get the new name for the variable
            x = self._new_name(phi, counter, stack)
            # Replace the phi function using the new name
            n.phi_functions[x] = n.phi_functions[phi]
            del n.phi_functions[phi]

            # Fill the parameters of successors phi functions
            for b in n.successors:
                if phi in b.phi_functions:
                    b.phi_functions[phi].append(x)

        # Rename all variables in the block
        for inst in n.instructions:
            for r in inst.registers_read():
                if (r, stack[r]) not in inst.ssa_read:
                    inst.ssa_read.append((r, stack[r][0]))
            for w in inst.registers_written():
                new_w = self._new_name(w, counter, stack)
                inst.ssa_written.append(new_w)

        # Continue the renaming process in the successors
        for n in n.dom_successors:
            self._rename_node(n, counter, stack)

        # Roll back the indexing
        for phi in n.phi_functions:
            for inst in n.instructions:
                if phi in inst.registers_written():
                    stack[phi[0]].pop()
            stack[phi[0]].pop()
