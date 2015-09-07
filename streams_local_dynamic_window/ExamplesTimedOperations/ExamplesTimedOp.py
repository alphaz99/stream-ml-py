if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
    else:
        from ..TimedOperators import *

from TimedOperators import *
from PrintFunctions import print_streams_recent_TimeAndValue

def example_1():
    print "example_1"

    def sum_of_list(lst):
        return sum([v.value for v in lst])

    def max_of_list(lst):
        return max([v.value for v in lst]) if lst != [] else None

    def sum_all_lists(list_of_lists):
        return sum(sum(v.value for v in list) for list in list_of_lists)

    x = Stream('x')
    y = Stream('y')

    def split_list_example(list_of_time_value):
        total_rapidly_increasing = 0.0
        total_slowly_increasing = 0.0
        for v in list_of_time_value:
            if v.value > v.time:
                total_rapidly_increasing += v.value
            else:
                total_slowly_increasing += v.value 
        return [total_rapidly_increasing, total_slowly_increasing]

    def g(lists_of_time_value):
        factor = 2
        r = sum(sum(v.value for v in list) for list in lists_of_time_value)
        return divmod(r, factor)

    window_size=16
    step_size=8
    window_start_time=0
    num_out_streams=2

    print "Lists of time and value."
    print "x and y are input lists."
    print "window_size = ", window_size
    print "step_size = ", step_size
    print "window_start_time = ", window_start_time
    print ""
    print "a = timed_op(sum_of_list, x, window_size, step_size)"
    print "b = timed_op(max_of_list, y, window_size, step_size)"
    print "c = timed_merge(sum_all_lists, [x, y], window_size, step_size)"
    print "d, e = timed_split(split_list_example, x, num_out_streams, window_size, step_size)"
    print "d has v.value > v.time and e has the others"
    print "v, w = timed_many_to_many(g, [x,y], num_out_streams, window_size, step_size)"
    print "v[i] = c[i]/2 and c[i] has the remainder"

    a = timed_op(sum_of_list, x, window_size, step_size)
    b = timed_op(max_of_list, y, window_size, step_size)
    c = timed_merge(sum_all_lists, [x, y], window_size, step_size)
    d, e = timed_split(split_list_example, x, num_out_streams, window_size, step_size)
    v, w = timed_many_to_many(g, [x,y], num_out_streams, window_size, step_size)

    a.set_name('a')
    b.set_name('b')
    c.set_name('c')
    d.set_name('d')
    e.set_name('e')
    v.set_name('v')
    w.set_name('w')

    x.extend([TimeAndValue(12, 5),
              TimeAndValue(13, 15),
              TimeAndValue(23, 12),
              TimeAndValue(25, 28),
              TimeAndValue(33, 30),
              TimeAndValue(40, 3)])
    y.extend([TimeAndValue(10, 8),
              TimeAndValue(15, 7),
              TimeAndValue(23, 15),
              TimeAndValue(28, 16),
              TimeAndValue(33, 27),
              TimeAndValue(40, 6)])
    print_streams_recent_TimeAndValue([x,y,a,b,c,d,e,v,w])

    ## x.extend([TimeAndValue(60, 44),
    ##           TimeAndValue(62, 46),
    ##           TimeAndValue(63, 47),
    ##           TimeAndValue(64, 52),
    ##           TimeAndValue(80, 60),
    ##           TimeAndValue(81, 80),
    ##           TimeAndValue(82, 81),
    ##           TimeAndValue(105, 81)])
    ## y.extend([TimeAndValue(45, 40),
    ##           TimeAndValue(72, 26),
    ##           TimeAndValue(73, 47),
    ##           TimeAndValue(84, 11),
    ##           TimeAndValue(88, 10),
    ##           TimeAndValue(105, 80)])
    ## print_streams_recent_TimeAndValue([x,y,a,b,c,d,e,u])
    

def main():
    example_1()

if __name__ == '__main__':
    main()
