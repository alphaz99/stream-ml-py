if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from Stream import *
from WindowOperators import window_split
from PrintFunctions import print_streams_recent

def example_1():
    print "example_1"
    factor = 2
    # f is a function from a window (a list) to
    # a list, where the result list has one element
    # for each output stream.
    # This example has two output streams.
    # The zeroth output stream gets the sum of the window
    # if the sum is divisible by factor, and 0 otherwise.
    # The first output stream is symmetric.
    def f(window):
        s = sum(window)
        if s % factor == 0:
            return [s, 0]
        else:
            return [0, s]

    x = Stream('x')
    # f is the function that operates on a window and produces a list.
    # x is the input stream.
    # window_split returns a list of num_out_streams of streams.
    [y, z] = window_split(f, in_stream=x,
                          num_out_streams=2,
                          window_size=2, step_size=2)
    y.set_name('y')
    z.set_name('z')
    
    x.extend([5, 11, 3, 8, 5, 5, 2, 3, 9, 21, 7])
    # The windows are [5, 11], [3, 8], [5, 5], [2, 3], [9, 21]
    # with sums 16, 11, 10, 5, 30 and the even numbers are 16, 10, 30
    # and so the y stream is [16, 0, 10, 0, 30] and
    # the x stream is [0, 11, 0, 5, 0]
    print_streams_recent([x, y, z])
    print""

    x.extend([8, 15, 18, 8, 20])
    print_streams_recent([x, y, z])

def main():
    example_1()

if __name__ == '__main__':
    main()
