from semantic_codec.metadata.rules import ConditionalFollowsCPSRModifier


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

        self._rules = [ConditionalFollowsCPSRModifier()]
        # self._errors = 0
        # for pos, val in self._program.items():
        #    self._errors += len(val) - 1

    def recover(self):
        """
        Start the recovery process
        """
        scores_changed = True
        while scores_changed:
            scores_changed = False
            for pos, instructions in self._program.items():
                if len(instructions) > 1:
                    for r in self._rules:
                        scores_changed |= r.recover(pos, self._program)