if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from Stream import *
from ListOperators import many_to_many
from PrintFunctions import print_streams_recent

def example_1():
    print "example_1"
    print "Calling signature:"
    print "many_to_many(f, in_streams, num_out_streams, state=None, call_streams=None)"
    print "Returns a list of num_out_streams streams."
    print "in_streams is a list of streams."
    print "List function: f(lists) where lists is a list of lists. "
    print "f() returns a list of num_out_streams lists. \n"

    print "In this example, many_to_many() returns two streams: multiples and nonmultiples."
    print "The input streams are summed element by element;"
    print "if this sum is a multiple  of factor(=2), then the sum appears in multiples"
    print "and otherwise it appears in nonmultiples."
    print "The input streams are x and y."

    factor = 2
    def f(lists):
        r = map(sum, zip(*lists))
        return [filter(lambda v: v % factor == 0, r),\
                filter(lambda v: v % factor != 0, r)]

    x = Stream('x')
    y = Stream('y')

    list_of_two_streams = many_to_many(f, [x,y], 2)
    multiples, nonmultiples = list_of_two_streams

    multiples.set_name('multiples')
    nonmultiples.set_name('nonmultiples')

    x.extend([5, 11])
    y.extend([2, 4, 5])
    print ""
    print "FIRST STEP"
    # Element by element sum of x and y is [5+2, 11+4].
    # Since these values are odd, they appear in nonmultiples,
    # and multiples is empty.
    print_streams_recent([x, y, multiples, nonmultiples])
    print""

    print "SECOND STEP"
    x.extend([9, 15, 19, 8, 20])
    y.extend([1, 3, 7])
    print_streams_recent([x, y, multiples, nonmultiples])

def main():
    example_1()

if __name__ == '__main__':
    main()

