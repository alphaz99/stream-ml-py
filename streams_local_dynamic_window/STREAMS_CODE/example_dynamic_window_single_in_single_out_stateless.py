if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from Stream import Stream, _no_value, _multivalue
from Operators import *

from Operators import stream_func

def main():
    # EXAMPLE FUNCTIONS ON WINDOWS
    # Functions have a single input: a list
    # which is the list of values in a window.
    # Functions return a scalar value, _no_value
    # or a list, _multivalue().

    min_window_size = 4
    max_window_size = 8
    step_size = 2

    input_stream = Stream('in')
    output_stream = Stream('out')

    current_window_size = 0
    steady_state = False
    reset = False
    state = [current_window_size, steady_state, reset]

    def f(lst, state):
        steady_state = state[1]
        return_value = sum(lst)
        if steady_state and return_value > 150:
            state[0] = 0 # Current window size
            state[1] = False # steady_state
            state[2] = True # reset
        return (sum(lst), state)

    dynamic_window_agent(
        f, input_stream, output_stream, state,
        min_window_size, max_window_size, step_size)

    print 'first phase'
    input_stream.extend(range(6))
    output_stream.print_recent()

    print 'second phase'
    input_stream.extend(range(6, 9, 1))
    output_stream.print_recent()

    print 'third phase'
    input_stream.extend(range(9, 36, 1))
    output_stream.print_recent()
 
if __name__ == '__main__':
    main()
