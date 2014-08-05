Multiprocessing and multiple progress bars
------------------------------------------

Well this was a success.

I've got multiple processes running at once in [parallel][my-multi]

[my-multi]: http://aaren.github.com/notes/2012/04/embarassingly_parallel_python

What I want to do here is have a progress bar for each process and
have these displayed nicely on the screen.

There is already a [decent module][progressbar] for printing
progress bars, so we're going to try and use that.

Writing stuff to specific places on the screen is a job for
[curses][], which is messy to use. Luckily I came across
[blessings][], which is an excellent clean wrapper around curses.

I've used blessings version 1.5 and progressbar version 2.3.

[progressbar]: https://pypi.python.org/pypi/progressbar/2.3-dev
[curses]: http://docs.python.org/2/howto/curses.html
[blessings]: https://pypi.python.org/pypi/blessings/

The main class in progressbar, ProgressBar, has an instantiation
argument `fd=sys.stderr` that is an object with a `write(string)`
method. This is how progressbar actually writes out to the screen.
By default, this happens by `sys.stderr.write('[----progress...]')`,
but we can supply our own writer.

Blessings works something like this (the [documentation][blessings]
is excellent btw):

```python
from blessings import Terminal

term = Terminal()

location = (0, 10)
text = 'blessings!'
print term.location(*location), text

# alternately,
with term.location(*self.location):
    print text
```

Progressbar works something like this:

```python
import time

from progressbar import ProgressBar

pbar.start()
for i in range(100):
    # mimic doing some stuff
    time.sleep(0.01)
    pbar.update(i)
pbar.finish()
```

We need to make something to connect progressbar and blessings.
Create an object that can write like this:

```python
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
```

Then we can put our progress bar wherever we want by feeding our
writer object to progressbar:

```python
def test_function(location):
    writer = Writer(location)
    pbar = ProgressBar(fd=writer)
    pbar.start()
    for i in range(100):
        # mimic doing some stuff
        time.sleep(0.01)
        pbar.update(i)
    pbar.finish()

x_pos = 0  # zero characters from left
y_pos = 10  # ten characters from top
location = (x_pos, y_pos)
test_function(location)
```

![Arbitrarily positioned progress bar](https://raw.github.com/aaren/multi_progress/master/single_progress_bar.png)

#### Multiprocessing ####

Now that we can put a progressbar where we choose it is fairly
trivial to extend this to multiprocessing.

Basic [multiprocessing][] usage, mapping a function `our_function`
onto a list of arguments `arg_list`:

```python
from multiprocessing import Pool

p = Pool()
p.map(our_function, arg_list)
p.close()
```

[multiprocessing]: http://docs.python.org/2/library/multiprocessing.html

In our case the function is `test_function` and the list of
arguments is a list of locations. For example, to have a progress
bar at the start of the line on the 2nd, 7th and 8th lines:

```python
locations = [(0, 1), (0, 6), (0, 7)]
p = Pool()
p.map(test_function, locations)
p.close()
```

![Parallel progress bars](https://raw.github.com/aaren/multi_progress/master/multi_progress_bar.png)

I've only got two active progress bars here because I've only got a
two core processor. `Pool()` defaults to making a number of worker
processes equal to the number of processors. Here is the same code
run on more cores with a load more locations:

![Lots of parallel progress bars](https://raw.github.com/aaren/multi_progress/master/more_multi_progress_bar.png)

#### Fullscreen output ####

You might notice that the examples above mess the screen up a bit.
This is because blessings, unlike curses, does not force a
fullscreen view that disappears on completion. We can tell blessings
to have this behaviour like this:

```python
with term.fullscreen():
    do_the_stuff_above()
```

I've made an [script][demo-script] that demonstrates all of the above.

[demo-script]: https://github.com/aaren/multi_progress/blob/master/multi_progress.py

And there you go, multiple independent progress bars implemented in
Python with not much hassle at all. This took me about 4 hours, blog
post included, thanks in large part to how easy [blessings][] makes
curses. 
