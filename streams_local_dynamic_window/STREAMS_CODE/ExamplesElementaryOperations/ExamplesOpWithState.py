"""This module contains examples of the op() function
where:
op(f,x) returns a stream where x is a stream, and f
is a function from a list and state to a list and state.
The state keeps track of the input stream up to the
current point.

Examples of the op() function, in its stateless form
are found in ExamplesOpNoState.py

The form of the call to op is:
op(f, in_stream, state, call_streams=None)
where f is the function from list, state to list, state,
and in_stream is the single input stream, and
call_streams is the list of streams that cause op()
to be invoked. If call_streams is None then the function
is invoked whenever a value is appended to in_stream.

"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ListOperators import stream_operator_stateful
from PrintFunctions import print_streams_recent

def example_1():
    print "example_1"

    # This examples uses the function total()
    # from list and state to a list and state.
    # The state is cumulative --- the cumulative
    # sum up to this point in the stream.
    # The result_list is the list of cumulative
    # values of the input list.
    
    def total(lst, cumulative):
        result_list = []
        for v in lst:
            cumulative += v
            result_list.append(cumulative)
        return (result_list, cumulative)

    x = Stream('x')
    # The initial state is 0.
    state = 0
    y = stream_operator_stateful(total, x, state)
    # Since call_streams is not specified, values will be
    # appended to y when values are appended to x.
    print "initial state = ", state
    print 'function on stream is total()'
    print 'This function computes the cumulative sum of the stream'
    print 'x is the input stream and y is the output stream.'
    print 'The state is the cumulative so far.'

    y.set_name('y')

    x.extend([3, 7])
    # Now the value of x is [3, 7], and so the
    # value of y is [3, 10], and the state is 10
    print_streams_recent([x, y])
    print ""

    x.extend([0, 11, 5])
    # Now the value of x is [3, 7, 0, 11, 5]
    # so the value of y is [3, 10, 10, 21, 26] and
    # the value of state is 26.
    print_streams_recent([x, y])


def example_2():
    print ""
    print "example_2"

    # This example uses the function:
    # avg_since_last_drop()
    # from a list and state to a list and state.
    # The output list is the list of averages of
    # the input list from the point that the value
    # in the input list drops by more than
    # drop_threshold.
    # The state is a tuple:
    # (time_since_last_drop, sum_since_last_drop,
    #  last_value, drop_threshold)
    # where time_since_last_drop is the number of
    # values since the last drop over the threshold,
    # sum_since_last_drop is the sum of the values
    # since the last drop over the threshold,
    # last_value is the most recent value read from
    # the input stream, and
    # drop_threshold is the specified threshold.

    def avg_since_last_drop(lst, state):
        time_since_last_drop, sum_since_last_drop,\
          last_value, drop_threshold = state
        result_list = []
        if lst == []:
            return (result_list, state)
        if last_value is None:
            last_value = lst[0]
        for v in lst:
            if last_value - v < drop_threshold:
                time_since_last_drop += 1
                sum_since_last_drop += v
            else:
                time_since_last_drop = 1
                sum_since_last_drop = v
            last_value = float(v)
            avg = sum_since_last_drop/float(time_since_last_drop)
            result_list.append(avg)
        return (result_list, state)

    x = Stream('x')
    time_since_last_drop = 0
    sum_since_last_drop = 0
    last_value = None
    drop_threshold = 100
    print "INITIAL VALUES"
    print 'time_since_last_drop = ', time_since_last_drop
    print 'sum_since_last_drop = ', sum_since_last_drop
    print 'last_value = ', last_value
    print 'drop_threshold = ', drop_threshold
    print ''
    state = (time_since_last_drop, sum_since_last_drop, last_value, drop_threshold)

    y = stream_operator_stateful(avg_since_last_drop, x, state)
    y.set_name('y')

    print 'first step'
    x.extend([16500, 16750, 16550, 16600, 16581])
    # The first drop of over drop_threshold is from 16750 to 16550
    # So, the output before that drop is the average for the window:
    # 16500.0, followed by average of (16500, 16750) = 16625.0
    # The output then starts computing averages afresh after the drop
    # starting with the value after the drop: 16550.0, 16575.0, 16577.0
    print_streams_recent([x, y])
    print ""

    print 'second step'
    x.extend([16400, 16500, 17002])
    # Another drop over the threshold of 100 occurs from 16581 to 16400
    # So, compute averages afresh from this point to get:
    # 16400.0, 16450.0, 16634.0
    print_streams_recent([x, y])

def example_3():
    def total(x_list, cumulative):
        result_list = []
        for v in x_list:
            cumulative += v
            result_list.append(cumulative)
        return (result_list, cumulative)

    def cumulative_stream(x_stream): return stream_operator_stateful(total, x_stream, state=0)

    x_stream = Stream('x_stream')
    y_stream = cumulative_stream(x_stream)
    y_stream.set_name('y_stream')
    # Appending messages to x_stream, we get:
    x_stream.extend([2, 4, -3])
    # Value of x_stream is [2, 4, -3]
    # y_stream becomes [2, 6, 3]
    print_streams_recent([x_stream, y_stream])
    # Appending more messages to x_stream, we get:
    x_stream.extend([-3, 5])
    # Value of x_stream is [2, 4, -3, -3, 5]
    # y_stream becomes [2, 6, 3, 0, 5]
    print_streams_recent([x_stream, y_stream])


def main():
    #example_1()
    #example_2()
    example_3()

if __name__ == '__main__':
    main()            
