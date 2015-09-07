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
from Stream import Stream, StreamArray, _no_value
from Operators import stream_func
import numpy as np


def main():
    # Functions: list,state -> list of lists, state
    def split_by_sensor_id(list_id_value, state):
        n_list, cum_list = state
        avg_list, next_n_list, next_cum_list = list(), list(), list()
        print 'list_id_value', list_id_value
        list_id_value = np.array(list_id_value)
        
        for id in [0,1]:
            print 'list_id_value[:,0]', list_id_value[:,0]
            values = list_id_value[np.where(
                list_id_value[:,0]==id)][:,1]
            b = np.zeros(len(values)+1)
            b[0] = cum_list[id]
            b[1:] = values
            b = np.cumsum(b)
            n_array = np.arange(n_list[id], n_list[id]+len(b), 1)
            avg = b[1:]/np.rint(n_array[1:])
            avg_list.append(avg)
            next_n_list.append(n_array[-1])
            next_cum_list.append(b[-1])
        next_state = (next_n_list, next_cum_list)
        return (avg_list, next_state)

    initial_state=([0, 0], [0.0, 0.0])
    stream_split_by_sensor_id = partial(stream_func, f_type='list',
                                     f=split_by_sensor_id, num_outputs=2,
                                     state=initial_state)

    # Create stream x, and give it name 'x'.
    x = Stream('input_0')

    id_0_average, id_1_average = stream_split_by_sensor_id(x)

    # Give names to streams. This is helpful in reading output.
    id_0_average.set_name('average of id_0 sensors in x')
    id_1_average.set_name('average of id_1 sensors in x')

    print
    print 'Adding ([(0,2), (0,4), (1,5), (1,1), (0,9)]'
    print 'to the input stream.'
    # Add values to the tail of stream x.
    x.extend([(0,2), (0,4), (1,5), (1,1), (0,9)])

    # Print recent values of the streams
    print
    print 'recent values of input streams'
    x.print_recent()

    print
    print 'recent values of output streams'
    id_0_average.print_recent()
    id_1_average.print_recent()

    print
    print
    print 'Adding ([(1,3), (1,7), (0,1), (1,9), (1,11), (0,4)])'
    print 'to the input stream.'
    # Add values to the tail of stream x.
    x.extend([(1,3), (1,7), (0,1), (1,9), (1,11), (0,4)])

    # Print recent values of the streams
    print 'recent values of input streams'
    print
    x.print_recent()

    print 'recent values of output streams'
    print
    id_0_average.print_recent()
    id_1_average.print_recent()

if __name__ == '__main__':
    main()
