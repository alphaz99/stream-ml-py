"""This module illustrates the use of call_stream.
A stream operation is carried out when a value is
appended to any call_stream.

This module illustrates call_streams using examples
of the op() function. For examples about op() see:
ExamplesOpNoState.py and
ExamplesOpWithState.py

These examples also show how streams are generated
from files and from lists. The times for opening
and closing files seem to slow down start up and
shut down.

The examples in this module are from:
ExamplesOpNoState.py.

For convenience, information from ExamplesOpNoState.py
is repeated here.

op(f,x) returns a stream where x is a stream, and f
is an operator on lists, i.e., f is a function from
a list to a list. These lists are of objects other than
streams and agents.

Function f must be stateless, i.e., for any lists u, v:
f(u.extend(v)) = f(u).extend(f(v))
(Stateful functions are given in OpStateful.py with
examples in OpStatefulExamples.py.)

Let f be a stateless operator on lists and let x be a stream.
If at some point, the value of stream x is a list u then at
that point, the value of stream op(f,x) is the list f(u).
If at a later point, the value of stream x is the list:
u.extend(v) then, at that point the value of stream op(f,x)
is f(u).extend(f(v)).
 
As a specific example, consider the following f():
def f(lst): return [w * w for w in lst]
If at some point in time, the value of x is [3, 7],
then at that point the value of op(f,x) is f([3, 7])
or [9, 49]. If at a later point, the value of x is
[3, 7, 0, 11, 5] then the value of op(f,x) at that point
is f([3, 7, 0, 11, 5]) or [9, 49, 0, 121, 25].

"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from Stream import *
from ListOperators import op
from PrintFunctions import print_stream_with_index, print_stream_recent
# clock_stream is a stream of 'ticks' at a specified rate
# and for a specified duration.
from ClockAgent import clock_stream, scheduler
# The module StreamOutputWhenCalled generates streams from lists
# and files when called by another stream such as a clock_stream.
from StreamOutputWhenCalled import stream_from_list, stream_from_file
import time

def example_1():
    # FUNCTIONS FROM LIST TO LIST

    # This example uses the following list operators:
    # functions from a list to a list.
    # f, g, h, r

    # Example A: function using list comprehension
    def f(lst):
        return [w*w for w in lst]

    # Example B: function using filter
    threshold = 2
    def predicate(w):
        return w > threshold
    def g(lst):
        return filter(predicate, lst)

    # Example C: function using map
    # Raise each element of the list to the n-th power.   
    n = 3
    def power(w):
        return w**n
    def h(lst):
        return map(power, lst)

    # Example D: function using another list comprehension
    # Discard any element of x that is not a
    # multiple of a parameter n, and divide the
    # elements that are multiples of n by n.
    n = 3
    def r(lst):
        result = []
        for w in lst:
            if w%n == 0: result.append(w/n)
        return result

    # CREATE A CLOCK STREAM
    trigger_stream = clock_stream(period=0.01,
                                  num_periods=12, name='trigger_stream')

    list_of_values = [ 3, 7, 0, 11, 5, 4, 6, 2, -1, 3, 2, 0, 4, 6, -3, -9, 8]
    x = stream_from_list(trigger_stream, list_of_values)
    x.set_name('x')
    y = stream_from_file(trigger_stream, file_name='ExampleFile.dat', step_size=1)
    y.set_name('y')

    # EXAMPLES OF OPERATIONS ON STREAMS
    
    # The output streams a, b, c, d obtained by
    # applying the list operators f, g, h, r to
    # stream x.
    state = None
    call_streams = [trigger_stream]
    a = op(f, x, state, call_streams)
    b = op(g, x, state, call_streams)
    c = op(h, y, state, call_streams)
    d = op(r, x, state, call_streams)

    # Name the output streams to label the output
    # so that reading the output is easier.
    a.set_name('a')
    b.set_name('b')
    c.set_name('c')
    d.set_name('d')
    
    print_stream_with_index(x)
    print_stream_with_index(trigger_stream)
    print_stream_with_index(a)
    print_stream_with_index(b)
    print_stream_with_index(c)
    print_stream_with_index(d)
    print_stream_with_index(y)


def main():
    print "Setting up streams and computations."
    example_1()
    print "Starting scheduler."
    scheduler.run()
    print "Finished scheduler run. Cleaning up."

if __name__ == '__main__':
    main()
