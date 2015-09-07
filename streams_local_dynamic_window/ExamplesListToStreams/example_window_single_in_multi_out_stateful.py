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
    def exp_smoothing_mean_std(lst, state):
        alpha = 0.8
        a = np.array(lst)
        print 'a.std()', a.std()
        m, s = state
        m = (1-alpha)*m + alpha*a.mean()
        s = (1-alpha)*s + alpha*a.std()
        state = (m,s)
        return ([m,s], state)

    x = Stream('x')

    y,z = stream_func(x, f_type='window', f=exp_smoothing_mean_std,
                    num_outputs=2, state=(0.0, 0.0),
                    window_size=3, step_size=3)
    y.set_name('y')
    z.set_name('z')
    
    x.extend([1, 2, 3, 4, 5])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

    x.extend([6, 12, 13, 14, 15])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

if __name__ == '__main__':
    main()
