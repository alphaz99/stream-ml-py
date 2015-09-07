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
from Stream import Stream
from Operators import stream_func

def main():
    # Functions: list -> element
    def mean(list_of_numbers):
        return sum(list_of_numbers)/float(len(list_of_numbers))

    def average_of_running_means(list_of_numbers, state):
        """ See example_element_single_in_single_out_stateful.py
        
        """
        current_value = mean(list_of_numbers)
        n, cum = state
        n += 1
        cum += current_value
        state = (n, cum)
        return (cum/float(n), state)

    # Functions: stream -> stream.
    # The n-th element of the output stream is f() applied to the n-th
    # elements of each of the input streams.
    # Function mean is defined above, and functions sum and max are the
    # standard Python functions.
    ## stream_sum = partial(stream_func, f_type='element', f=sum, num_outputs=1)
    ## stream_max = partial(stream_func, f_type='element', f=max, num_outputs=1)    
    stream_running_mean = partial(stream_func, f_type='element',
                                  f=average_of_running_means, num_outputs=1,
                                  state = (0,0.0))
    stream_mean = partial(stream_func, f_type='element',
                                  f=mean, num_outputs=1)

    # Create stream x, and give it name 'x'.
    x = Stream('input_0')
    y = Stream('input_1')
    z = Stream('input_2')

    # u is the stream returned by stream_sum([x,y])  and
    # v is the stream returned by stream_max([x,y])
    # w is the stream returned by stream_mean([x,y]).
    # u[i] = sum(x[i],y[i])
    # v[i] = max(x[i],y[i])
    # w[i] = mean(x[i],y[i])    
    u = stream_running_mean([x,y,z])
    ## v = stream_max([x,y,z])
    w = stream_mean([x,y,z])


    # Give names to streams u, v, and w. This is helpful in reading output.
    u.set_name('running mean of inputs')
    ## v.set_name('max of inputs')
    w.set_name('mean of inputs')

    print
    print 'Adding [3, 5, 8], [1, 7, 2], [2, 3] to 3 input streams'
    # Add values to the tail of stream x.
    x.extend([3, 5, 8])
    y.extend([1, 7, 2])
    z.extend([2, 3])

    print
    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print
    print 'recent values of output streams'
    print 'stateless stream function:'
    w.print_recent()
    print 'stateful stream function:'    
    u.print_recent()


    print
    print
    print 'Adding [4, 6, 2], [2, 3, 8], [5, 3, 0, -1] to 3 input streams'
    # Add more values to the tail of stream x.
    x.extend([4, 6, 2])
    y.extend([2, 3, 8])
    z.extend([5, 3, 0, -1])

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print
    print 'recent values of output streams'
    print 'stateless stream function:'    
    w.print_recent()
    print 'stateful stream function:'        
    u.print_recent()

if __name__ == '__main__':
    main()

