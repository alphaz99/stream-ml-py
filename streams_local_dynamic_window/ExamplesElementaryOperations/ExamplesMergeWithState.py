if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from Stream import *
from ListOperators import merge
from PrintFunctions import print_streams_recent

def example_1():
    print "example_1"
    print "This example shows how multiple streams are merged into a single stream"
    print ""
    print "merge(f, in_streams, state, call_streams=None): f is a function"
    print "from a list of lists and state a to a list and state"
    print "in_streams is a list of streams \n"
    print "In this example, state is the cumulative of the zeroth input stream"
    print "The output stream is the sum of the state and the value in the first input stream."
    print "The input streams are x and y. The output stream is a."
    print ""

    def f(two_lists, state):
        result_list = []
        for j in range(len(two_lists[0])):
            result_list.append(state+two_lists[0][j]+two_lists[1][j])
            state += two_lists[0][j]
        return (result_list, state)

    x = Stream('x')
    y = Stream('y')

    a = merge(f, in_streams=[x,y], state=0)
    a.set_name('a')

    x.extend([5, 11])
    y.extend([2, 4, 5])
    print "FIRST STEP"
    # The cumulative for x is [5, 16]. So the output is [5+2, 16+4]
    print_streams_recent([x, y, a])
    print""

    x.extend([9, 15, 19, 8, 20])
    y.extend([1, 3, 7])
    print "SECOND STEP"
    # The cumulative for x is [5, 16, 25, 40, 59, 67, 87]
    # So, the output is [5+2, 16+4, 25+5, 40+1, 59+3, 67+7]
    print_streams_recent([x, y, a])

def main():
    example_1()

if __name__ == '__main__':
    main()

