"""
File containing the classes representing rules
"""
from semantic_codec.architecture.arm_instruction import AOpType


def from_instruction_list_to_dict(instructions):
    result = {}
    for inst in instructions:
        result[inst.position] = [inst]
    return result


class DefaultProbabilisticModel(object):
    """
    Class containing the values assigned to the probabilities model variables
    """

    def __init__(self):
        self.ALWAYS_AFTER_CPSR = 0.1
        self.NEAR_CONDITIONALS_ARE_EQUALS = 0.5


class Rule(object):
    def __init__(self, program, model=None):
        self._model = DefaultProbabilisticModel() if model is None else model
        self._program = program

    def recover(self, position):
        """
        Tries to recover an instruction in a given position of a program
        :param position: Position where the instruction is
        :param program: Program to recover
        :param model: Probabilistic model
        :return: The amount of instructions discarded
        """
        pass

    def _get_instruction_at(self, adrr, program):
        inst = None
        if adrr in adrr:
            inst = program[adrr]
        return inst

    def _update_scores(self, new_scores, instructions):
        """
        Determine if the scores assigned to the instructions by the rules have changed
        """
        i, k = 0, str(self.__class__)
        updated = False
        for inst in instructions:
            if k not in inst.scores_by_rule or new_scores[i] != inst.scores_by_rule[k]:
                inst.scores_by_rule[k] = new_scores[i]
                updated = True
            i += 1

        return updated


class ConditionalCount(Rule):
    """
    Class that enforces that the conditional count in the program abides to the metadata conditional count
    """

    def __init__(self, program, model=None, collector=None):
        super().__init__(program, model)
        if collector is None:
            raise RuntimeError("Must set a collector")
        self._collector = collector
        self._remaining_conditionals = []
        self._total_remaining = 0

    def _compute_remaining_conditionals(self):

        if len(self._remaining_conditionals) == 0:
            self._remaining_conditionals.extend(self._collector.conditional_count)
            for inst in self._program.values():
                if len(inst) == 1 and not inst[0].is_undefined:
                    self._remaining_conditionals[inst[0].conditional_field] -= 1

    def recover(self, address):
        self._compute_remaining_conditionals()
        if self._total_remaining == 0:
            return False

        # Score assigned to each conditional field
        scores = []
        for i in range(0, 17):
            scores.append(self._remaining_conditionals[i] / self._total_remaining)

        candidates, i = self._program[address], 0
        new_score = [0] * len(candidates)
        for c in candidates:
            new_score[i] = scores[c.conditional_field]
            i += 1
        return self._update_scores(new_score, candidates)


class ConditionalFollowsCPSRModifier(Rule):
    """
    Class that enforces the rule that a conditional instruction must follow another capable of modifying the CPSR register
    """

    def recover(self, position):
        # Get previous instruction
        addr = position - 4
        prev_inst = self._program[addr] if addr in self._program else None
        # Get posterior instruction
        addr = position + 4
        post_inst = self._program[addr] if addr in self._program else None

        # Score assigned to each conditional field
        conditional_score = [0.0] * 16

        if prev_inst is not None and len(prev_inst) == 1:
            if prev_inst[0].modifies_flags():
                # Assign a BAD score to the conditional 'always' if we have
                # a previous instruction that modifies the flags
                conditional_score[AOpType.COND_ALWAYS] -= self._model.ALWAYS_AFTER_CPSR
            else:
                # Assign a good score to the conditional equal to the previous instruction
                conditional_score[prev_inst[0].conditional_field] += self._model.NEAR_CONDITIONALS_ARE_EQUALS
        if post_inst is not None and len(post_inst) == 1:
            # Assign a good score to the conditional equal to the posterior instruction
            conditional_score[post_inst[0].conditional_field] += self._model.NEAR_CONDITIONALS_ARE_EQUALS

        instructions, i = self._program[position], 0
        new_score = [0] * len(instructions)
        for c in instructions:
            new_score[i] = conditional_score[c.conditional_field]
            i += 1
        return self._update_scores(new_score, instructions)


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
