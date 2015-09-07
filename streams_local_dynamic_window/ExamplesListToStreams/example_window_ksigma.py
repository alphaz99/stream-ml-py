if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from Stream import Stream 
from Operators import stream_func
import numpy as np

LTA_SIZE = 4
GAP_SIZE = 2
STA_SIZE = 3
WINDOW_SIZE = LTA_SIZE + GAP_SIZE + STA_SIZE
STEP_SIZE = 1
EPSILON = 1e-10

def ksigma(lst):
    lst = np.array(lst)
    lta_region = lst[:LTA_SIZE]
    sta_region = lst[-STA_SIZE:]
    # Avoid division by 0
    return (abs(sta_region.mean() - lta_region.mean())/
            max(lta_region.std(), EPSILON))


def main():
    print "example_1"
    print

    x = Stream('x')
    y = stream_func(x, f_type='window', f=ksigma,
                    num_outputs=1,  window_size=WINDOW_SIZE,
                    step_size=STEP_SIZE)

    y.set_name('y')
 
    x.extend(range(20))
    x.print_recent()
    y.print_recent()
    print

    x.extend(range(20, 0, -1))
    x.print_recent()
    y.print_recent()
    print
    

if __name__ == '__main__':
    main()
