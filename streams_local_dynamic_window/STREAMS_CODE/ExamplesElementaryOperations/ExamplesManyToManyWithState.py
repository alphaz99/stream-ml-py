if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from ListOperators import many_to_many_stateful
from PrintFunctions import print_streams_recent
from Agent import *

def example_1():
    print "example_1"
    print "Calling signature:"
    print "many_to_many_stateful(f, in_streams, num_out_streams, state, call_streams=None)"
    print "Returns a list of num_out_streams streams."
    print "in_streams is a list of streams.\n"
    print "List function: f(lists, state) where lists is a list of lists, and "
    print "state is a tuple."
    print "f() returns a list of num_out_streams lists and the next state. \n"

    print "THIS EXAMPLE, many_to_many_stateful() returns two streams: multiples and nonmultiples."
    print "If the cumulative of both input streams is a multiple of factor then"
    print "the cumulative appears in multiples and otherwise it appears in nonmultiples."
    print "The input streams are x and y."

    factor = 2
    def f(two_lists, state):
        x = two_lists[0]
        y = two_lists[1]
        a = []
        b = []
        for j in range(min(len(x), len(y))):
            state = x[j] + y[j] + state
            if state % factor == 0:
                a.append(state)
            else:
                b.append(state)
        return ([a, b], state)

    x = Stream('x')
    y = Stream('y')

    multiples, nonmultiples = many_to_many_stateful(f, [x,y], 2, state=0)
    multiples.set_name('multiples')
    nonmultiples.set_name('nonmultiples')

    x.extend([5, 1])
    y.extend([2, 4, 5])
    print_streams_recent([x, y, multiples, nonmultiples])
    print""

    x.extend([6, 5, -5, 8, 2])
    y.extend([0, -1, 5])
    print_streams_recent([x, y, multiples, nonmultiples])
    return

def example():
    def f_list(list_of_lists, state):
        length = min(len(l) for l in list_of_lists)
        list_of_lists.append([state]*length)
        return map(sum, zip(*list_of_lists))
    x = [1, 2, 3]
    y = [25, 26, 27]
    f_list([x,y], state=5)
        


    
def example_2():
    def f_stream(list_of_streams):

        def f_list(list_of_lists, state):
            sum_list = map(sum, zip(*list_of_lists))
            if not sum_list:
                return ([[], []], state)
            cumulative_list = [0]*len(sum_list)
            cumulative_list[0] = sum_list[0] + state
            for i in range(1, len(sum_list)):
                cumulative_list[i] = cumulative_list[i-1] + sum_list[i]
            state = cumulative_list[-1] if cumulative_list else 0
            first_list = filter(lambda v: v % 2 == 0, cumulative_list)
            second_list = filter(lambda v: v % 2 != 0, cumulative_list)
            return ([first_list, second_list], state)

        return many_to_many_stateful(f_list, list_of_streams, num_outputs=2, state=0)

    print 'example_2'
    x = Stream('x')
    y = Stream('y')

    multiples, nonmultiples = f_stream([x,y])
    multiples.set_name('multiples')
    nonmultiples.set_name('nonmultiples')

    x.extend([5, 1])
    y.extend([2, 4, 5])
    print_streams_recent([x, y, multiples, nonmultiples])
    print""

    x.extend([6, 5, -5, 8, 2])
    y.extend([0, -1, 5])
    print_streams_recent([x, y, multiples, nonmultiples])
    return
    
def main():
    #example_1()
    example_2()
    #example()

if __name__ == '__main__':
    main()


def f_stream(list_of_streams):
    def f_list(list_of_lists, state):
        sum_list = map(sum, zip(*list_of_lists))
        if not sum_list:
            return ([[], []], state)
        cumulative_list = [0]*len(sum_list)
        cumulative_list[0] = sum_list[0] + state
        for i in range(1, len(sum_list)):
            cumulative_list[i] = cumulative_list[i-1] + sum_list[i]
        state = cumulative_list[-1] if cumulative_list else 0
        first_list = filter(lambda v: v % 2 == 0, cumulative_list)
        second_list = filter(lambda v: v % 2 != 0, cumulative_list)
        return ([first_list, second_list], state)
    return many_to_many_stateful(f_list, list_of_streams, state=0)
