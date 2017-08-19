import sys
from math import log

from semantic_codec.metadata.recuperator import probabilistic_rules


class SolutionQuality(object):
    """
    Class that computes the solution's quality so far. The quality of the answer is mostly how small is the solution,
    however it has other parameters as the highest depth.
    """

    def __init__(self, program, original_program):

        self._highest_depth_bin = {}

        # The highest depth in the solution (i.e. the worst place a correct answer has)
        self._highest_depth = None

        # Compute the number of possible solutions
        self._solution_count = -1

        # Amount of addresses with 2, 4, 8, 16, 32... candiates
        self._solution_count_bins = None

        self._program = program

        self._original_program = original_program

        # Number of bits required to represent the solution
        self._solution_size = None

    @property
    def solution_size(self):
        if self._solution_count <= -1:
            self._count_solutions(self._program)
        if self._solution_count == 0:
            return 0
        return self._solution_size

    @property
    def highest_depth(self):
        if self._highest_depth is None:
            self.evaluate()
        return self._highest_depth

    @property
    def solution_count_bins(self):
        if not self._solution_count_bins:
            self._count_solutions(self._program)
        return self._solution_count_bins

    @property
    def solution_count(self):
        if self._solution_count == -1:
            self._count_solutions(self._program)
        return self._solution_count

    def _count_solutions(self, program):
        bins = {}
        max_v = 0
        for v in program.values():
            k = len(v)
            if k > max_v:
                max_v = k
            if k in bins:
                bins[k] += 1
            else:
                bins[k] = 1

        i = 1
        amount = 0
        for i in bins.keys():
            amount += i ** bins[i]

        self._solution_count = amount
        self._solution_count_bins = bins
        self._solution_size = 0

        for k, v in bins.items():
            if k > 1:
                self._solution_size += (log(k, 2)) * bins[k]

    def evaluate(self):
        self._solution_count = self._count_solutions(self._program)

        # Change the probabilistic function to one more continous
        self._highest_depth = 0
        self._highest_depth_bin = {}
        max_addr_bin = {}
        max_addr = 0
        for k in range(0, len(self._original_program)):
            if self._original_program[k].ignore:
                continue
            addr = self._original_program[k].position
            v = self._program[addr]
            min_encoding = sys.maxsize
            for inst in v:
                if inst.encoding < min_encoding:
                    min_encoding = inst.encoding
            v.sort(key=lambda x: 0 if min_encoding == 0 else (x.score() * 1000000000 + min_encoding/ x.encoding), reverse=True)
            #v.sort(key=lambda x: x.score(), reverse=True)# * 1000000000 + x.encoding / max_encoding, reverse=True)

            # Count the depth bin

            i = 0
            ln = len(v)
            while i < ln and str(v[i]) != str(self._original_program[k]):
                i += 1

            if not ln in self._highest_depth_bin:
                self._highest_depth_bin[ln] = 0

            r = (i+1) / ln
            if ln > 0:
                if r > self._highest_depth_bin[ln]:
                    self._highest_depth_bin[ln] = r
                    max_addr_bin[ln] = addr
                if r > self._highest_depth:
                    self._highest_depth = r
                    max_addr = addr
        print('[INFO] Highest Depth at address > {}'.format(hex(max_addr)))
        print('[INFO] Highest Depth at address bin > {}'.format(max_addr_bin))
        print('[INFO] Highest Depth bin > {}'.format(self._highest_depth_bin))

    def report(self):
        a = self
        print('[INFO]: Solutions: {}'.format(a.solution_count_bins))
        print('[INFO]: Solutions size: {}'.format(a.solution_size))
        print('[INFO]: Solutions count: {}'.format(a.solution_count))

