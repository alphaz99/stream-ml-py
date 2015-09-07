"""This module contains examples of stream_func where f_type
is 'element' and stream_func has a list of multiple input streams,
a single output stream, and the operation is stateless. These
examples must have a LIST of input streams and not a single
input stream.

The functions on static Python data structures are of the form:
    list -> element

"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream, _no_value
from Operators import stream_func
import numpy as np


def main():
    # Functions: list of lists -> list
    a = 1
    def inrange_and_outlier(x_and_y_lists):
        x, y = x_and_y_lists
        x = np.array(x)
        y = np.array(y)
        if abs(y.mean() - x.mean()) <= a*x.std():
            # in range
            return ([y.mean(), _no_value])
        else:
            # (x,y) is an outlier
            # Return _no_value for the outlier stream.
            return ([_no_value, y.mean()])

    # Functions: stream -> stream.
    # The n-th element of the output stream is f() applied to the n-th
    # elements of each of the input streams.
    # Function mean is defined above, and functions sum and max are the
    # standard Python functions.

    # Create stream x, and give it name 'x'.
    x = Stream('input_0')
    y = Stream('input_1')

    
    inrange_stream, outlier_stream = stream_func([x,y], f_type='window',
                                                 f=inrange_and_outlier,
                                                 num_outputs=2,
                                                 window_size=3,
                                                 step_size=3)
                                                 

    # Give names to streams. This is helpful in reading output.
    inrange_stream.set_name('inrange')
    outlier_stream.set_name('outlier')

    print
    # Add values to the tail of stream x.
    x.extend([1, 2, 3])
    y.extend([1, 2])

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    print
    # Add more values to the tail of stream x.
    x.extend([4, 5])
    y.extend([3, 8, 9, 10])

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    x.extend([6])

    
    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()
    


    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    print
    print 'Adding [4, 6, 2], [2, 3, 8], [5, 3, 0, -1] to 3 input streams'
    # Add more values to the tail of stream x.
    x.extend([4, 6, 2])
    y.extend([2, 14, 8, 9])


    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()


if __name__ == '__main__':
    main()

