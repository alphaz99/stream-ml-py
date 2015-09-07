if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from Stream import Stream, _no_value, _multivalue
from Operators import *
from functools import partial

from Operators import stream_func

import pdb

def main():
    # EXAMPLE FUNCTIONS ON WINDOWS
    # Functions have a single input: a list
    # which is the list of values in a window.
    # Functions return a scalar value, _no_value
    # or a list, _multivalue().

    min_window_size = 2
    max_window_size = 11
    step_size = 2

    input_stream = Stream('in')
    # output_stream = Stream('out')

    current_window_size = 0
    steady_state = False
    reset = False
    state = [current_window_size, steady_state, reset]

    def f(lst, state):
        print lst
        return (lst, state)

    f_stream = partial(dynamic_window_func, f = f, state = state, min_window_size = min_window_size, max_window_size = max_window_size, step_size = step_size)

    output_stream = f_stream(inputs = input_stream)
    # output_stream = dynamic_window_func(
        # f, input_stream, state,
        # min_window_size, max_window_size, step_size)

    for i in range(1, 15):
        print "Adding ", i
        input_stream.extend([i])
        if i == 10:
            state[2] = True
        # output_stream.print_recent()
        print "\n"
 
if __name__ == '__main__':
    main()
