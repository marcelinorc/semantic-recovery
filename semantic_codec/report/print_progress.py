# Print iterations progress
import sys

class TextProgressBar(object):

    def __init__(self, iteration, total, prefix='', suffix='',
                 decimals=1, bar_length=100, print_dist=10):
        self.iteration = iteration
        self._total = total
        self._decimals = decimals
        self._bar_length = bar_length
        self._print_dist = print_dist
        self.prefix = prefix
        self.suffix = suffix
        self._prev_percent = None

    def _go_to_end(self):
        self.iteration = self._total
        self._prev_percent = 100
        self._print_last_iteration()

    def _print_last_iteration(self):
            bar = '█' * self._bar_length
            sys.stdout.write('\r%s |%s| %s%s %s' % (self.prefix, bar, 100, '%', self.suffix)),
            sys.stdout.write('\n')

    def progress(self):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            bar_length  - Optional  : character length of bar (Int)
        """
        if self._prev_percent is not None and self.iteration == self._total:
            return
        elif self.iteration + self._print_dist >= self._total:
            self._go_to_end()
            return

        p = 100 * (self.iteration / float(self._total))
        self.iteration += 1
        if self._prev_percent is not None and p - self._prev_percent < self._print_dist:
            return

        str_format = "{0:." + str(self._decimals) + "f}"
        percents = str_format.format(p)
        filled_length = int(round(self._bar_length * self.iteration / float(self._total)))
        bar = '█' * filled_length + '-' * (self._bar_length - filled_length)
        sys.stdout.write('\r%s |%s| %s%s %s' % (self.prefix, bar, percents, '%', self.suffix)),

        if self.iteration + self._print_dist >= self._total:
            self._go_to_end()
        sys.stdout.flush()

        self._prev_percent = p