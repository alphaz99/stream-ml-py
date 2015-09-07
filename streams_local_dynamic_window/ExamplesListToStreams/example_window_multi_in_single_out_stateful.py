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
    def sum_diff_of_means(list_of_two_lists, cumulative):
        a, b = list_of_two_lists
        cumulative += np.mean(a) - np.mean(b)
        return (cumulative, cumulative)
    x = Stream('x')
    y = Stream('y')
    z = stream_func([x,y], f_type='window', f=sum_diff_of_means,
                    num_outputs=1, state = 0,
                    window_size=2, step_size=2)
    z.set_name('z')
    
    x.extend([3,5])
    y.extend([2])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

    x.extend([11,15])
    y.extend([4, -10, -12])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

if __name__ == '__main__':
    main()
    
    
                    
