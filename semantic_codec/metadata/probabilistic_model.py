
class DefaultProbabilisticModel(object):
    """
    Class containing the values assigned to the probabilities model variables
    """
    def __init__(self):
        # Indicates the probability of a branching instruction happening after a flag register write
        self.branch_after_cpsr = 0.6
        # Indicates the probability that two consecutive instructions have the same conditional
        self.near_conditionals_are_equals = 0.4
        # Indicates the chance of a jump being invalid if it lies inside the program
        self.jump_is_valid = 0.1
