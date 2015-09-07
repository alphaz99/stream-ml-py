"""This module contains examples of the op() function
where:
op(f,x) returns a stream where x is a stream, and f
is an operator on lists, i.e., f is a function from
a list to a list. These lists are of lists of arbitrary
objects other than streams and agents.

Function f must be stateless, i.e., for any lists u, v:
f(u.extend(v)) = f(u).extend(f(v))
(Stateful functions are given in OpStateful.py with
examples in ExamplesOpWithState.py.)

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
from ListOperators import *
from PrintFunctions import print_streams_recent

def example_1():
    print "example_1"
    print "op(f, x): f is a function from a list to a list"
    print "x is a stream \n"

    # FUNCTIONS FROM LIST TO LIST

    # This example uses the following list operators:
    # functions from a list to a list.
    # f, g, h, r


    # Example A: function using list comprehension
    def f(lst): return [w*w for w in lst]

    # Example B: function using filter
    threshold = 6
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

    
    


    # EXAMPLES OF OPERATIONS ON STREAMS
    
    # The input stream for these examples
    x = Stream('x')

    print 'x is the input stream.'
    print 'a is a stream consisting of the squares of the input'
    print 'b is the stream consisting of values that exceed 6'
    print 'c is the stream consisting of the third powers of the input'
    print 'd is the stream consisting of values that are multiples of 3 divided by 3'
    print 'newa is the same as a. It is defined in a more succinct fashion.'
    print 'newb has squares that exceed 6.'
    print ''

    # The output streams a, b, c, d obtained by
    # applying the list operators f, g, h, r to
    # stream x.
    a = op(f, x)
    b = op(g, x)
    c = op(h, x)
    d = op(r, x)

    # You can also define a function only on streams.
    # You can do this using functools in Python or
    # by simple encapsulation as shown below.
    def F(x): return op(f,x)
    def G(x): return op(g,x)
    newa = F(x)
    newb = G(F(x))
    # The advantage is that F is a function only
    # of streams. So, function composition looks cleaner
    # as in G(F(x))

    # Name the output streams to label the output
    # so that reading the output is easier.
    a.set_name('a')
    newa.set_name('newa')
    b.set_name('b')
    newb.set_name('newb')
    c.set_name('c')
    d.set_name('d')

    # At this point x is the empty stream:
    # its value is []
    x.extend([3, 7])
    # Now the value of x is [3, 7]
    print "FIRST STEP"
    print_streams_recent([x, a, b, c, d, newa, newb])
    print ""

    x.extend([0, 11, 15])
    # Now the value of x is [3, 7, 0, 11, 15]
    print "SECOND STEP"
    print_streams_recent([x, a, b, c, d, newa, newb])

def main():
    example_1()

if __name__ == '__main__':
    main()
