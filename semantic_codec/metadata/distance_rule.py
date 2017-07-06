import sys

from semantic_codec.architecture.arm_instruction import ARMInstruction, AReg
from semantic_codec.metadata.probabilistic_model import DefaultProbabilisticModel
from semantic_codec.metadata.rules import Rule


class RegisterDistanceRule(Rule):
    """
    Class that enforces that a register read is never farther than what the metadata said.
    It also favors the register write-read closer to the mean
    """

    def __init__(self, program, model=None, collector=None):
        super().__init__(program, model, collector)
        if not collector:
            raise RuntimeError("A collector is required for this rule to work")
        self._collector = collector

    def _get_storages_read(self, candidates):
        """
        Returns a list of all storages used by the candidates
        """
        result = []
        for c in candidates:
            result.extend([r for r in c.storages_read() if not r in result])
        return result

    def _get_storages_written(self, candidates):
        """
        Returns a list of all storages used by the candidates
        """
        result = []
        for c in candidates:
            result.extend([r for r in c.storages_written() if not r in result])
        return result


class RegisterWriteDistance(RegisterDistanceRule):
    """
    Class that enforces that a register write is never farther than what the metadata said.
    It also favors the register write-read closer to the mean
    """
    pass

class RegisterReadDistanceProbability(RegisterDistanceRule):
    """
    Gives a more robust probabilistic score of all registers of an instruction being read in thsi particular
    address
    """

    def recover(self, position):
        pass


class RegisterReadDistance(RegisterDistanceRule):

    @staticmethod
    def short_name():
        return "REG_DIST"

    def recover(self, position):
        EPSILON = 0.00000000000001
        INST_SIZE = ARMInstruction.INST_SIZE_BYTES

        # candidate instructions
        candidates = self._program[position]
        # Scores that each candidates at this position is going to be awarded
        score = [0] * len(candidates);

        updated = False

        dist_min = self._collector.storage_min_dist
        dist_max = self._collector.storage_max_dist

        for c in candidates:

            # Assume all instructions are well defined
            if c.ignore:
                self._update_candidate_score(c, 0.0)
                continue
            elif len(c.storages_used()) == 0:
                updated |= self._update_candidate_score(c, EPSILON)
                continue

            storages = c.storages_read()
            # Find the range in which the registers write live:
            min_d, max_d = sys.maxsize, -sys.maxsize
            for v in storages:
                min_d = dist_min[v] if v in dist_min and dist_min[v] < min_d else min_d
                max_d = dist_max[v] if v in dist_max and dist_max[v] > max_d else max_d

            # We are going backwards, so in fact prev_max is < than prev
            # Go backwards searching for registers writting to the registers we read from
            prev_pos = position - INST_SIZE * min_d # Position of the first previous instruction
            prev_pos_max = position - INST_SIZE * max_d # Position of the last previous instruction (going backwards)
            register_score = [EPSILON] * AReg.STORAGE_COUNT

            candidate_score = 0

            while prev_pos >= prev_pos_max and candidate_score < 1:
                if prev_pos not in self._program:
                    prev_pos -= 4
                    continue
                prev_candidates = self._program[prev_pos]
                for prev_c in prev_candidates:

                    if prev_c.ignore:
                        # Can't analyze undefined instructions
                        continue

                    c_reg_score = [EPSILON] * AReg.STORAGE_COUNT
                    prev_w = prev_c.storages_written()
                    # Find the score this previous candidate contributes to the candidate being evaluated
                    for w in prev_w:
                        if w in storages:
                            c_reg_score[w] += 1 / (len(prev_w) * self.candidate_count(prev_candidates))
                    try:
                        register_score[w] = max(register_score[w], c_reg_score[w])
                    except UnboundLocalError:
                        print("What??")
                    except IndexError:
                        print("W:"+str(w))

                # Find the score of the candidate so far
                s = 0
                for r in storages:
                    try:
                        s += register_score[r]
                    except IndexError:
                        print("R:"+str(r))

                candidate_score = max(s / len(storages), candidate_score)

                if candidate_score >= 1:
                    updated |= self._update_candidate_score(c, 1)
                    break
                else:
                    # Keep going backwards
                    prev_pos -= INST_SIZE
                    # Have we updated any score so far?
                    updated |= self._update_candidate_score(c, candidate_score)

        return updated
