if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from Stream import Stream, _no_value, _multivalue
from Operators import *

from Operators import stream_func

import pdb

def main():
    # EXAMPLE FUNCTIONS ON WINDOWS
    # Functions have a single input: a list
    # which is the list of values in a window.
    # Functions return a scalar value, _no_value
    # or a list, _multivalue().

    min_window_size = 3
    max_window_size = 7
    step_size = 2

    input_stream = Stream('in')
    output_stream = Stream('out')

    current_window_size = 0
    steady_state = False
    reset = False
    state = [current_window_size, steady_state, reset]

    def f(lst, state):
        if sum(lst) > 100:
            # state[2] is set to True to reset the window
            state[2] = True
        return (lst, state)

    dynamic_window_agent(
        f, input_stream, output_stream, state,
        min_window_size, max_window_size, step_size)

    ## input_stream.extend(range(5))

    for i in range(0, 10):
        input_stream.extend([i])
        input_stream.print_recent()
        output_stream.print_recent()
        print "\n"

    for i in range(2,4,1):
        input_stream.extend(range(10*i,10*i+5,1))
        print
        input_stream.print_recent()
        print
        output_stream.print_recent()
        print
            
 
if __name__ == '__main__':
    main()
