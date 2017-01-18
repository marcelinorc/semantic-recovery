from semantic_codec.metadata.rules import Rule


class RegisterDistanceRule(Rule):
    """
    Class that enforces that a register read is never farther than what the metadata said.
    It also favors the register write-read closer to the mean
    """
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


class RegisterReadDistance(RegisterDistanceRule):

    def recover(self, position):
        # candidate instructions
        candidates = self._program[position]
        # Score that the candidates is going to be awarded
        score = [0] * len(candidates)

        for c in candidates:
            position, keep = position - 4, True
            while keep:
                # Keep going backwards until we find enough a storage written for a 1 probability
                # or we go away from the maximum distance
                if position in self._program:
                    prev_cand = self._program[position]
                    if len(prev_cand) == 1:
                        pass
                else:
                    keep = False