if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from ListOperators import *
from PrintFunctions import print_streams_recent

def example_1():
    print "example_1"
    print "Calling signature:"
    print "many_to_many(f, in_streams, num_out_streams, state, call_streams=None)"
    print "Returns a list of num_out_streams streams."
    print "in_streams is a list of streams.\n"
    print "List function: f(lists, state) where lists is a list of lists, and "
    print "state is a tuple."
    print "f() returns a list of num_out_streams lists and the next state. \n"

    print "THIS EXAMPLE, many_to_many() returns two streams: multiples and nonmultiples."
    print "If the cumulative of both input streams is a multiple of factor then"
    print "the cumulative appears in multiples and otherwise it appears in nonmultiples."
    print "The input streams are x and y."

    factor = 2
    def f(two_lists, state):
        x = two_lists[0]
        y = two_lists[1]
        a = []
        b = []
        for j in range(len(x)):
            state = x[j] + y[j] + state
            if state % factor == 0:
                a.append(state)
            else:
                b.append(state)
        return ([a, b], state)

    x = Stream('x')
    y = Stream('y')

    multiples, nonmultiples = many_to_many(f, [x,y], 2, state=0)
    multiples.set_name('multiples')
    nonmultiples.set_name('nonmultiples')

    x.extend([5, 1])
    y.extend([2, 4, 5])
    print_streams_recent([x, y, multiples, nonmultiples])
    print""

    x.extend([6, 5, -5, 8, 2])
    y.extend([0, -1, 5])
    print_streams_recent([x, y, multiples, nonmultiples])

def main():
    example_1()

if __name__ == '__main__':
    main()

