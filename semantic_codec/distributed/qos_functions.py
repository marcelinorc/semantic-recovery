class MockQoSFunction(object):

    def __init__(self):
        self.probability = 0.1

        self._counter = 0

    def run(self, new_instruction, address):
        if self._counter == 2:
            self._counter = 0
            return True
        else:
            self._counter += 1
            return False
