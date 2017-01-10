from semantic_codec.architecture.arm_instruction import AReg
from pygraph.classes.digraph import digraph
from semantic_codec.static_analysis.cfg import CFGBlock
from semantic_codec.static_analysis.dominators import build_dominator_tree


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
            read = inst.storages_read()
            written = inst.storages_written()

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

    # place the phi functions in the node
    for x in globals_vars:
        if x in blocks:
            work_list = blocks[x]
            i = 0
            while i < len(work_list):
                for d in work_list[i].dom_frontier:
                    if d.kind != CFGBlock.END:
                        ssa_x = (x, 0)
                        if ssa_x not in d.phi_functions:
                            d.phi_functions[ssa_x] = []# * len(d.predecessors)
                        if d not in work_list:
                            work_list.append(d)
                i += 1

    return globals_vars

#
#class SSAVar(object):
#    """
#    Class representing the variables in the SSA form
#    """
#    def __init__(self, base, index):
#        self.base = base
#        self.index = index
#
#    def __hash__(self):
#        # Find hash value based on the `data`
#        return 31 * self.base + self.index
#
#    def __eq__(self, other):
#        return self.base == other.base and self.index == other.index
#
#    def __ne__(self, other):
#        return not (self.__eq__(other))
#
#    def __str__(self):
#        return "{}.{}".format(self.base, self.index)
#
#    def __repr__(self):
#        return self.__str__()


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
        # Rename the variables into their SSA form
        self._rename_vars(global_vars)
        # After the renaming is possible to know if there are any dead phi nodes.
        # We must eliminate them, as they make the SSA Value dep very dirty
        self._remove_dead_phi()
        # build the value dependency graph
        return self._build_value_dependency_graph()

    def _build_value_dependency_graph(self):
        d = digraph()
        for n in self._graph:
            for phi, val in n.phi_functions.items():
                if not phi in d:
                    d.add_node(phi)
                for v in val:
                    if not v in d:
                        d.add_node(v)
                    if not d.has_edge((v, phi)):
                        d.add_edge((v, phi))
            for inst in n.instructions:
                for w in inst.ssa_written:
                    if w not in d:
                        d.add_node(w)
                    for r in inst.ssa_read:
                        if r not in d:
                            d.add_node(r)
                        if not d.has_edge((r, w)):
                            d.add_edge((r, w))
        return d

    @staticmethod
    def _new_name(n, counter, stack):
        """
        Increases the counter for a given variable and returns a tuple containing the variable name and ssa index
        """
        var = n[0]
        i = counter[n[0]]
        i += 1
        stack[var].insert(0, i)
        counter[var] = i
        return var, i

    def _rename_vars(self, global_vars):
        """
        Rename the variables in the SSA
        """
        counter = {}
        stack = {}
        for v in range(0, AReg.STORAGE_COUNT):
            counter[v] = 0
            stack[v] = [0]

        self._rename_node(self._root, counter, stack)

    def _rename_node(self, n, counter, stack):
        """
        Rename the variables in SSA form in the nodes of the CFG
        """
        # First rename all phi variables
        new_phi_dict = {}
        for phi, val in n.phi_functions.items():
            # Get the new name for the variable
            new_phi_dict[self._new_name(phi, counter, stack)] = val
        n.phi_functions = new_phi_dict

        # Rename all variables in the block
        for inst in n.instructions:
            for r in inst.storages_read():
                ssa_r = (r, stack[r][0])
                if ssa_r not in inst.ssa_read:
                    inst.ssa_read.append(ssa_r)
            for w in inst.storages_written():
                ssa_w = self._new_name((w, 0), counter, stack)
                inst.ssa_written.append(ssa_w)

        # Append the phi variable to the parameters of following phi functions
        for b in n.successors:
            for phi, val in b.phi_functions.items():
                var = phi[0]
                val.append((var, stack[var][0]))

        # Continue the renaming process in the successors
        for n in n.dom_successors:
            self._rename_node(n, counter, stack)

        # Roll back the indexing
        for phi in n.phi_functions:
            var = phi[0]
            for inst in n.instructions:
                if var in inst.storages_written():
                    stack[var].pop()
            stack[var].pop()

    def _remove_dead_phi(self):
        """
        Remove the dead phi nodes
        """
        for n in self._graph:
            rem = []
            for phi in n.phi_functions:
                var, index = phi
                keep_it, probably_dead, i = True, True, 0 # Should we keep the phi?
                while i < len(n.instructions) and probably_dead and keep_it:
                    inst = n.instructions[i]
                    for ssa_r in inst.ssa_read:
                        if var == ssa_r[0] and index == ssa_r[1]:
                            # the phi is not dead, break
                            probably_dead = False
                            break

                    if probably_dead:
                        for ssa_w in inst.ssa_written:
                            if var == ssa_w[0] and index < ssa_w[1]:
                                keep_it = False
                                break
                    i += 1
                if not keep_it:
                    rem.append(phi)
            for phi in rem:
                del n.phi_functions[phi]



