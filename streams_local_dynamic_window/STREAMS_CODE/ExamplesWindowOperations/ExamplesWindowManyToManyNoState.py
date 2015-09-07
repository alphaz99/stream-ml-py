if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from Stream import *
from WindowOperators import window_many_to_many
from PrintFunctions import print_streams_recent

def example_1():
    print "example_1"
    factor = 2

    # f takes windows as input, where windows is a list
    # in which each element is a window (a list).
    # The output of f is a list with an element for each
    # output stream.
    # This example is for a list with two output streams.
    # Sum corresponding elements of all input windows.
    # If the sum of the corresponding windows is divisible by
    # factor, then that sum is added to the zeroth output
    # stream, and otherwise it is added to the first output
    # stream.
    def f(windows):
        r = map(sum, zip(*windows))
        multiples = filter(lambda v: v % factor == 0, r)
        nonmultiples = filter(lambda v: v % factor != 0, r)
        return [sum(multiples), sum(nonmultiples)]

    x = Stream('x')
    y = Stream('y')

    list_of_two_streams = window_many_to_many(f,
                                              in_streams=[x,y],
                                              num_out_streams=2,
                                              window_size=2,
                                              step_size=2)
    multiples, nonmultiples = list_of_two_streams

    multiples.set_name('multiples')
    nonmultiples.set_name('nonmultiples')

    x.extend([5, 11])
    y.extend([2, 4, 5])
    # The windows for the two input streams x, y are:
    # [5, 11] and [2, 4] respectively.
    # The sums of the input streams, element by element are:
    # [5+2, 11+4] or [7, 15]. Since these elements are not
    # multiples of factor, the multiples stream outputs [0] 
    # and the nonmultiples stream outputs [7+15] or [22]
    print_streams_recent([x, y, multiples, nonmultiples])
    print""

    x.extend([9, 15, 19, 8, 20])
    y.extend([1, 3, 7])
    # The new windows for x are [9, 15], [19, 8] and
    # for y are [5, 1], [3, 7].
    # The sums of the input streams, element by element are:
    # [14, 16], [22, 15].
    # The multiples stream outputs [14+16], [22], and the
    # nonmultiples stream outputs [0], [15].
    print_streams_recent([x, y, multiples, nonmultiples])
    print""

    x.extend([19, 10, 11, 28, 30])
    y.extend([1, 3, 7, 13, 17, 19, 20, 40, 80])
    print_streams_recent([x, y, multiples, nonmultiples])
    print""


def main():
    example_1()

if __name__ == '__main__':
    main()


