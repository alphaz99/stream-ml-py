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
    def max_and_min(lst):
        return (max(lst), min(lst))

    x = Stream('x')

    y,z = stream_func(x, f_type='window', f=max_and_min,
                    num_outputs=2, window_size=2, step_size=2)
    y.set_name('y')
    z.set_name('z')
    
    x.extend([3,5])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

    x.extend([11,15])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

if __name__ == '__main__':
    main()
