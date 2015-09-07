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
    # Functions: list, state -> list, state
    delta = 0.5
    def inrange_and_outlier(x_and_y_lists, state):
        a, b, n, x_sum, y_sum, xx_sum, xy_sum = state
        x_array, y_array = np.array(x_and_y_lists)
        l = len(x_array)
        if not l:
            return (x_and_y_lists, state)
        n_array = np.arange(n, n+l,1)
        x_sum_array = x_sum + np.cumsum(x_array)
        y_sum_array = y_sum + np.cumsum(y_array)
        xy_sum_array = xy_sum + np.cumsum(x_array*y_array)        
        xx_sum_array = xx_sum + np.cumsum(x_array*x_array)
        a_array = ((xy_sum_array - x_sum_array*y_sum_array/np.rint(n_array))/
                   (xx_sum_array - x_sum_array*x_sum_array/np.rint(n_array)))
        b_array = y_sum_array/np.rint(n_array) - a*x_sum_array/np.rint(n_array)

        z_list = zip(*x_and_y_lists)
        outliers = np.where(abs(a_array*x_array + b_array - y_array) > delta*abs(y_array))
        inrange = np.where(abs(a_array*x_array + b_array - y_array) <= delta*abs(y_array))
        outliers_array = np.hstack([x_array[outliers], y_array[outliers]])
        #outliers_array = np.array([x_array[outliers], y_array[outliers]])
        inrange_array = np.array([x_array[inrange], y_array[inrange]])
        #return_array = np.array([inrange_array, outliers_array])
        
        state = (a_array[-1], b_array[-1], n_array[-1],
                 x_sum_array[-1], y_sum_array[-1],
                 xx_sum_array[-1], xy_sum_array[-1])
        return ([inrange_array, outliers_array], state)


    # Functions: stream -> stream.
    # The n-th element of the output stream is f() applied to the n-th
    # elements of each of the input streams.
    # Function mean is defined above, and functions sum and max are the
    # standard Python functions.
    # state = a, b, n, x_sum, y_sum, xx_sum, xy_sum
    # xx_sum is set to a small value to avoid division by 0.0
    # n is set to 2 to reflect that the regression is assumed to have
    # been running for at least 2 points.
    state=(1.0, 0.0, 2, 0.0, 0.0, 0.001, 0.0)
    inrange_and_outlier_streams = partial(stream_func, f_type='list',
                                         f=inrange_and_outlier,
                                         num_outputs=2, state=state)

    # Create stream x, and give it name 'x'.
    x = Stream('input_0')
    y = Stream('input_1')

    
    inrange_stream, outlier_stream = inrange_and_outlier_streams([x,y])

    # Give names to streams u, v, and w. This is helpful in reading output.
    inrange_stream.set_name('inrange')
    outlier_stream.set_name('outlier')

    print
    # Add values to the tail of stream x.
    x.extend(range(10, 15, 1))
    y.extend(range(10, 15, 1))

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    print
    print 'Adding [15, 16, ...19], [150, 160,..190] to 2 streams.'
    # Add more values to the tail of stream x.
    x_list = range(15, 20, 1)
    y_list = [10*v for v in x_list]
    
    x.extend(x_list)
    y.extend(y_list)

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    print
    print 'The regression parameters take some time to adjust'
    print 'to the new slope. Initially x = y, then x = 10*y'


if __name__ == '__main__':
    main()

