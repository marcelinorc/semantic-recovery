"""
File containing the classes representing rules
"""
from semantic_codec.architecture.arm_instruction import AOpType
from semantic_codec.metadata.probabilistic_model import DefaultProbabilisticModel


def from_instruction_list_to_dict(instructions):
    """
    Turn the list of instructions into a dictionary indexed by position
    """
    result = {}
    for inst in instructions:
        result[inst.position] = [inst]
    return result


class Rule(object):
    def __init__(self, program, model=None, collector=None):
        self._model = DefaultProbabilisticModel() if model is None else model
        self._program = program
        self._collector = collector

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






# ------------------------------------------------------

class ConditionalFollowsCPSRModifier(Rule):
    """
    Class that enforces the rule that a conditional instruction must follow
    another capable of modifying the CPSR register.

    Also it favors instrucions having the same conditional that the nearest ones
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
                conditional_score[AOpType.COND_ALWAYS] -= self._model.always_after_cpsr
            else:
                # Assign a good score to the conditional equal to the previous instruction
                conditional_score[prev_inst[0].conditional_field] += self._model.near_conditionals_are_equals
        if post_inst is not None and len(post_inst) == 1:
            # Assign a good score to the conditional equal to the posterior instruction
            conditional_score[post_inst[0].conditional_field] += self._model.near_conditionals_are_equals

        i, new_score = 0, []
        for c in self._program[position]:
            new_score.append(conditional_score[c.conditional_field])
        return self._update_scores(new_score, self._program[position])
