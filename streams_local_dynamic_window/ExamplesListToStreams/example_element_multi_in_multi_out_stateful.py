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


def main():
    
    def inrange_and_outlier_streams_adaptive(
            xy_streams, delta):

        def inrange_and_outlier(x_and_y, state):
            x, y = x_and_y
            a, b, n, x_sum, y_sum, xx_sum, xy_sum = state
            # Compute output
            if abs(a*x + b - y) > delta:
                # (x,y) is an outlier.
                # The streams returned by stream func are:
                # [inrange stream outlier stream]
                # Return _no_value for the inrange stream.
                return_list = [_no_value, x_and_y]
            else:
                # (x,y) is inrange.
                # Return _no_value for the outlier stream.
                return_list = [x_and_y, _no_value]

            # Compute the next state
            n += 1
            x_sum += x
            y_sum += y
            xy_sum += x*y
            xx_sum += x*x
            a = (xy_sum - x_sum*y_sum/float(n))/(xx_sum - x_sum*x_sum/float(n))
            b = y_sum/float(n) - a*x_sum/float(n)
            state = a, b, n, x_sum, y_sum, xx_sum, xy_sum
            return (return_list, state)

        # We assume here that an earlier computation was carried
        # out to fit a straight line over 2 points (0.0, 0.0) and
        # (1.0, 1.0). This prior computation is not shown here.
        # So, n, x_sum, y_sum, xx_sum, xy_sum are
        # 2, 1.0, 1.0, 1.0, 1.0, respectively.
        initial_state = (1.0, 0.0, 2, 1.0, 1.0, 1.0, 1.0)
        return stream_func(
            inputs=xy_streams,
            f_type='element',
            f=inrange_and_outlier,
            num_outputs=2,
            state=initial_state)
            
    # Create streams x and y, and give it
    # names 'input_0', 'input_1'
    x = Stream('input_0')
    y = Stream('input_1')

    # Create streams inrange_stream, outlier_stream
    inrange_stream, outlier_stream = \
      inrange_and_outlier_streams_adaptive(xy_streams=[x,y],
                                           delta=0.5)

    # Give names to inrange_stream, outlier_stream.
    # This is helpful in reading output.
    inrange_stream.set_name('inrange')
    outlier_stream.set_name('outlier')

    print
    # Add values to the tail of streams x and y.
    x.extend(range(10, 15, 1))
    y.extend(range(10, 15, 1))

    # Print recent values of the streams
    print
    print 'Recent values of input streams'
    x.print_recent()
    y.print_recent()

    print
    print 'Recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    print
    print 'Adding [15, 16, ...19], [16, 7,..20] to x and y streams.'
    # Add more values to the tail of stream x.
    x.extend(range(15, 25, 1))
    y.extend(range(16, 26, 1))

    # Print recent values of the streams
    print
    print 'Recent values of input streams'
    x.print_recent()
    y.print_recent()

    print
    print 'Recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    print
    print 'The regression parameters take some time to adjust'
    print 'to the new slope. Initially x = y, then x = y+1'


if __name__ == '__main__':
    main()

