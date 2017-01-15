
class DefaultProbabilisticModel(object):
    """
    Class containing the values assigned to the probabilities model variables
    """
    def __init__(self):
        self.always_after_cpsr = 0.1
        self.near_conditionals_are_equals = 0.5