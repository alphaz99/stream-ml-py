if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from functools import partial
from Stream import Stream 
from Operators import stream_func
import numpy as np



def main():
    print "example_1"
    print "example function from list to value: mean_and_sigma() "
    window_size = 2
    step_size = 2
    print "window_size = ", window_size
    print "step_size = ", step_size
    print ""
    
    window_sum = partial(stream_func, f_type='window', f=sum,
                         num_outputs=1,  window_size=2,
                         step_size=2)

    x = Stream('x')
    # x is the in_stream.
    # sum() is the function on the window

    z = stream_func(x, f_type='window', f=np.mean, num_outputs=1,  window_size=2,
                    step_size=2)

    
    y = window_sum(x)
    y.set_name('y')
    z.set_name('z')
 

    x.extend([5, 11])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

    x.extend([9, 15, 19, 8, 20])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print
    
    x.extend([19, 10, 11, 28, 30])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print
    

if __name__ == '__main__':
    main()
