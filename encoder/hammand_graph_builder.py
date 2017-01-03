# Builds a graph where two nodes joined by an edge represents two numbers for which their hammand distances are equal 1
class HammandGraphBuilder(object):
    def __init__(self, space_size_exponent=8):
        # The space size exponent. Our encoding space size is equal to 2^_space_size_exponent
        # 256 elements in our encoding space
        self._space_size_exponent = space_size_exponent
        self._graph = []

    def build_graph(self):
        print("graph G {")
        max_v = 2 ** self._space_size_exponent
        for x in range(0, max_v):
            y = 1
            while y <= max_v - 1:
                self.edge(x, x ^ y)
                y *= 2
        print("}")

    def edge(self, x, y):
        # Print the binary
        inv_edge = '"{0:b}" -- "{1:b}"'.format(y, x)
        if inv_edge not in self._graph:
            edge = '"{0:b}" -- "{1:b}"'.format(x, y)
            self._graph.append(edge)
            print(edge + ';')
