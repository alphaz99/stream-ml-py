if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from Stream import *
from WindowOperators import window_merge
from PrintFunctions import print_streams_recent

def example_1():
    print "example_1"
    factor = 2
    def f(windows):
        r = map(sum, zip(*windows))
        multiples = filter(lambda v: v % factor == 0, r)
        return sum(multiples)

    x = Stream('x')
    y = Stream('y')

    # In window_merge: f is a function that operates on a lis
    # of windows. [x, y] are the streams that are merged.
    # window_size and step_size specify the size of the sliding
    # window and how the window is moved at each step.
    # Sum x, y element by element. If the sum is a multiple
    # of factor (factor=2), then return the sum for the window.
    z = window_merge(f, [x,y], window_size=2, step_size=2)
    z.set_name('z')

    x.extend([5, 11])
    y.extend([2, 4, 5])
    # Since window_size=2 and step_size=2, the first windows are:
    # for x: [5, 11], and for y: [2, 4]. So, the sum is [7, 15].
    # Since 7, 15 are not divisible by factor (2), set z to [0]
    print_streams_recent([x, y, z])
    print""

    x.extend([9, 15, 19, 8, 20])
    y.extend([1, 3, 7])
    # The next windows are: for x: [9, 15], [19, 8], and
    # for y: [5, 1], and [3, 7]. So, the sums are [14, 16]
    # and [22, 15]. Since 14, 16 are divisible by factor return
    # their sum: 30. Since 22 is divisible by factor and 15 is not
    # return 22. So the new value of z is [0, 30, 22].
    print_streams_recent([x, y, z])
    print""

    x.extend([19, 10, 11, 28, 30])
    y.extend([1, 3, 7, 13, 17, 19, 20, 40, 80])
    print_streams_recent([x, y, z])
    print""


def main():
    example_1()

if __name__ == '__main__':
    main()


