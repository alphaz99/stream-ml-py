if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from Stream import *
from ListOperators import merge_stateless
from PrintFunctions import print_streams_recent

def example_1():
    print "example_1"
    print "This example shows how multiple input streams are merged into a single output stream."
    print "op(f, in_streams): f is a function from a list of lists to a list"
    print "in_streams is a list of streams \n"
    print "In this example, the input streams are x and y."
    print "In this example, the function f() computes element by element sums of the input streams."
    print ""

    def f(in_streams):
        return map(sum, zip(*in_streams))

    x = Stream('x')
    y = Stream('y')

    a = merge_stateless(f, [x,y])
    a.set_name('a')

    x.extend([5, 11])
    y.extend([2, 4, 5])
    print "FIRST STEP"
    print_streams_recent([x, y, a])
    print""

    x.extend([9, 15, 19, 8, 20])
    y.extend([1, 3, 7])
    print "SECOND STEP"
    print_streams_recent([x, y, a])

def example_2():
    
    def F(in_streams):
        def f(in_streams):
            return map(sum, zip(*in_streams))
        return merge(f, in_streams)

    x = Stream('x')
    y = Stream('y')

    a = F([x,y])
    a.set_name('a')

    x.extend([5, 11])
    y.extend([2, 4, 5])
    print "FIRST STEP"
    print_streams_recent([x, y, a])
    print""

    x.extend([9, 15, 19, 8, 20])
    y.extend([1, 3, 7])
    print "SECOND STEP"
    print_streams_recent([x, y, a])


def example_3():
    
    def G(in_lists):
        def f(in_lists):
            return map(sum, zip(*in_lists))
        return merge_stateless(f, in_lists)

    x = Stream('x')
    y = Stream('y')

    a = G([x,y])
    a.set_name('a')

    x.extend([5, 11])
    y.extend([2, 4, 5])
    print "FIRST STEP"
    print_streams_recent([x, y, a])
    print""

    x.extend([9, 15, 19, 8, 20])
    y.extend([1, 3, 7])
    print "SECOND STEP"
    print_streams_recent([x, y, a])

    
def main():
    ## print "EXAMPLE_1"
    ## example_1()
    ## print ""
    ## print "EXAMPLE_2"
    ## example_2()
    print "EXAMPLE_3"
    example_3()

if __name__ == '__main__':
    main()

