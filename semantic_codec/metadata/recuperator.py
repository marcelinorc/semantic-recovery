from semantic_codec.metadata.counting_rules import ConditionalCount, InstructionCount, RegisterCount
from semantic_codec.metadata.distance_rule import RegisterReadDistance
from semantic_codec.metadata.rules import ControlFlowBehavior


class Recuperator(object):
    """
    Class in charge of recuperating the lost bits of information using the metadata sent
    """

    def __init__(self, collector, program):
        """
        Builds the recuperator
        :param collector: Metadata collector
        :param program: Dictionary where the key is the memory position of an instruction
                        and the value a list of possibles instructions.
        """
        self._collector = collector
        self._program = program

        # self._errors = 0
        # for pos, val in self._program.items():
        #    self._errors += len(val) - 1
        self.passes = 1

    def recover(self):
        """
        Start the recovery process
        """
        # scores_changed = True
        # while scores_changed:
        # scores_changed = False
        for i in range(0, self.passes):
            rules = [ControlFlowBehavior(self._program),
                     ConditionalCount(self._program, collector=self._collector),
                     InstructionCount(self._program, collector=self._collector),
                     RegisterCount(self._program, collector=self._collector),
                     RegisterReadDistance(self._program, collector=self._collector)]
            for pos, instructions in self._program.items():
                if len(instructions) > 1:
                    for r in rules:
                        r.current_pass = i
                        r.recover(pos)
                # Find the mean value of scores:
                # k = len(instructions)
                if self.passes > 1 and len(instructions) > 1:
                    # k = 0
                    for inst in instructions:
                        for v in inst.scores_by_rule.values():
                            if v <= 0 and not inst.ignore:
                                inst.ignore = True
#                    if k == 0:
#                        s, k = 0, 0
#                        for inst in instructions:
#                            if not inst.ignore:
#                                s += inst.score()
#                                k += 1
#                        if k > 0:
#                            s /= k
#                            for inst in instructions:
#                                if inst.score() < s:
#                                    inst.ignore = True
#