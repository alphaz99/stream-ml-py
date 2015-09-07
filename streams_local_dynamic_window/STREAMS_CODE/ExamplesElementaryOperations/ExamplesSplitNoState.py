if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ListOperators import split_stateless
from PrintFunctions import print_streams_recent

def example_1():
    print "example_1"
    print "Calling signature:"
    print "split(f, in_stream, num_out_streams, state=None, call_streams=None)"
    print "Returns a list of num_out_streams streams."
    print "List function: f(lst) where lst is a list. "
    print "f() returns a list of num_out_streams lists."
    print "in_stream is a single stream. \n"

    print "In this example, split() returns two streams: multiples and nonmultiples of factor."
    print "x is the input stream."

    factor = 2
    print "factor = ", factor
    def f(lst):
        return [filter(lambda n: n%factor == 0, lst), \
                filter(lambda n: n%factor != 0, lst)]

    x = Stream('x')

    #list_of_two_streams =split(f, x, 2)
    list_of_two_streams =split_stateless(f, x, 2)
    multiples, nonmultiples = list_of_two_streams

    multiples.set_name('multiples')
    nonmultiples.set_name('nonmultiples')

    x.extend([5, 11])
    print ""
    print "FIRST STEP"
    print_streams_recent([x, multiples, nonmultiples])
    print""

    x.extend([9, 15, 19, 8, 20])
    print "SECOND STEP"
    print_streams_recent([x, multiples, nonmultiples])

def main():
    example_1()

if __name__ == '__main__':
    main()

