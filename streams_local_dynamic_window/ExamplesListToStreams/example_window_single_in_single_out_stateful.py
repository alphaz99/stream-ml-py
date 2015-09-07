if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from functools import partial
from Stream import Stream 
from Operators import stream_func
import numpy as np
import random



def main():
    def max_of_std(lst, state):
        a = np.array(lst)
        state = max(a.std(), state)
        return (state, state)
    print "example_1"
    print "example function from list to value: mean_and_sigma() "
    window_size = 10
    step_size = 10
    print "window_size = ", window_size
    print "step_size = ", step_size
    print ""

    x = Stream('x')
    # x is the in_stream.
    # sum() is the function on the window

    z = stream_func(x, f_type='window', f=max_of_std, num_outputs=1, state=0.0,
                    window_size=window_size, step_size=step_size)

    z.set_name('z')
 

    x.extend([random.random() for i in range(30)])
    x.print_recent()
    z.print_recent()


if __name__ == '__main__':
    main()
