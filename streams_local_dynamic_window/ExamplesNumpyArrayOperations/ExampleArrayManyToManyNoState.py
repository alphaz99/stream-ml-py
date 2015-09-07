if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

#from Stream import *
from ListOperators import many_to_many
from PrintFunctions import print_streams_recent, print_stream_recent
import numpy as np

def f(two_arrays):
    return [np.hypot(two_arrays[0], two_arrays[1]),
            two_arrays[0]/two_arrays[1]]

def example_1():
    x = StreamArray('x')
    y = StreamArray('y')

    list_of_two_stream_arrays = many_to_many(f, [x,y], 2)
    hypotenuses, tangents = list_of_two_stream_arrays
    hypotenuses.set_name('hypotenuse_stream')
    tangents.set_name('tangent_stream')

    x.extend([3.0, 4.0])
    y.extend([4.0, 3.0])
    print_streams_recent([x, y,hypotenuses, tangents])

def main():
    example_1()

if __name__ == '__main__':
    main()


    
