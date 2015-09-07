if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from Stream import *
from ListOperators import split
from PrintFunctions import print_streams_recent

def example_1():
    print "example_1"
    print "Calling signature:"
    print "split(f, in_stream, num_out_streams, state, call_streams=None)"
    print "Returns a list of num_out_streams streams."
    print "List function: f(lst, state) where lst is a list. "
    print "f() returns a list of num_out_streams lists and state"
    print "in_stream is a single stream. \n"

    print "THIS EXAMPLE"
    print "The input stream is x and the output streams are a and b."
    print "The input stream is fed to one of the output streams until"
    print "the next even number (multiple of factor=2); at that point"
    print "the stream is fed to the other output stream."
    print "This function switches x between a and b where the switch is triggered"
    print "by an event: namely the appearance of an even value."
    print ""

    factor = 2

    def f(lst, state):
        a = []
        b = []
        for j in range(len(lst)):
            if (lst[j]+state) % factor == 0:
                state = 1
                a.append(lst[j])
            else:
                state = 0
                b.append(lst[j])
        return ([a,b], state)


    x = Stream('x')

    a, b =split(f, in_stream=x, num_out_streams=2, state=0)
    a.set_name('a')
    b.set_name('b')

    x.extend([4, 5, 10, 11, 13, 16, 9])
    print "FIRST STEP"
    print_streams_recent([x, a, b])
    print""

    x.extend([15, 19, 8, 7, 20, 21])
    print "SECOND STEP"
    print_streams_recent([x, a, b])

def main():
    example_1()

if __name__ == '__main__':
    main()

