from __future__ import division

import sys
import time
import random
from multiprocessing import Pool

from blessings import Terminal
from progressbar import ProgressBar

term = Terminal()


class Writer(object):
    """Create an object with a write method that writes to a
    specific place on the screen, defined at instantiation.

    This is the glue between blessings and progressbar.
    """
    def __init__(self, location):
        """
        Input: location - tuple of ints (x, y), the position
                          of the bar in the terminal
        """
        self.location = location

    def write(self, string):
        with term.location(*self.location):
            print(string)


def test(location):
    """Test with a single bar.

    Input: location - tuple (x, y) defining the position on the
                      screen of the progress bar
    """
    # fd is an object that has a .write() method
    writer = Writer(location)
    pbar = ProgressBar(fd=writer)
    # progressbar usage
    pbar.start()
    for i in range(100):
        # do stuff
        # time taken for process is function of line number
        # t_wait = location[1] / 100
        # time take is random
        t_wait = random.random() / 50
        time.sleep(t_wait)
        # update calls the write method
        pbar.update(i)

    pbar.finish()


def test_bars(locations):
    """Test with multiple bars.

    Input: locations - a list of location (x, y) tuples
    """
    writers = [Writer(loc) for loc in locations]
    pbars = [ProgressBar(fd=writer) for writer in writers]
    for pbar in pbars:
        pbar.start()

    for i in range(100):
        time.sleep(0.01)
        for pbar in pbars:
            pbar.update(i)

    for pbar in pbars:
        pbar.finish()


def test_parallel(locations):
    """Test case with multiprocessing.

    Input: locations - a list of location (x, y) tuples

    Think of locations as a list of jobs. Each job is going
    to be processed by the single bar test.
    """
    pool = Pool()
    pool.map(test, locations)
    pool.close()


def main():
    if len(sys.argv) == 4 and sys.argv[1] == 'single':
        x = int(sys.argv[2])
        y = int(sys.argv[3])
        print("Printing at ({x}, {y})".format(x=x, y=y))
        location = (x, y)
        test(location)
    elif len(sys.argv) == 4 and sys.argv[1] == 'multi':
        first = int(sys.argv[2])
        last = int(sys.argv[3])
        locations = [(0, i) for i in range(first, last)]
        test_bars(locations)
    elif len(sys.argv) == 4 and sys.argv[1] == 'parallel_single':
        line1 = int(sys.argv[2])
        line2 = int(sys.argv[3])
        locations = [(0, line1), (0, line2)]
        test_parallel(locations)
    elif len(sys.argv) == 4 and sys.argv[1] == 'parallel_multi':
        first = int(sys.argv[2])
        last = int(sys.argv[3])
        locations = [(0, i) for i in range(first, last)]
        test_parallel(locations)
    else:
        raise UserWarning


def usage():
    """Print help to the screen"""
    usage_str = """Usage:
        python multi.py single x_pos y_pos
        python multi.py multi first_line last_line
        python multi.py parallel_single line_one line_two
        python multi.py parallel_multi first_line last_line
        """
    print(usage_str)


if __name__ == '__main__':
    try:
        with term.fullscreen():
            main()
    except UserWarning:
        usage()
