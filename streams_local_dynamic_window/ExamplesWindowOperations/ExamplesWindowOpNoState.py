if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from Agent import *
from Stream import *
from WindowOperators import window_op
from PrintFunctions import print_streams_recent

# Each of these functions operates on a list
# or a Numpy array.
# Return the average of the list
def mean(lst):
    if lst == []: return []
    return sum(lst)/float(len(lst))

# Return (average, standard deviation) of the list
def mean_and_sigma(lst):
    EPSILON = 1.E-10
    if lst == []: return []
    print 'lst =', lst
    mean = sum(lst)/float(len(lst))
    second_moment = sum(v*v for v in lst)/float(len(lst))
    variance = second_moment - mean*mean
    # Dealing with numerical error
    if variance < 0.0 and variance > -EPSILON: variance = 0.0
    if variance < 0.0:
        raise Exception('ExamplesOpNoState: mean_and_sigma: negative variance')
    sigma = math.sqrt(variance)
    return (mean, sigma,)

def standard_deviation(lst):
    EPSILON = 1.E-10
    if lst == []: return []
    mean = sum(lst)/float(len(lst))
    second_moment = sum(v*v for v in lst)/float(len(lst))
    variance = second_moment - mean*mean
    # Dealing with numerical error
    if variance < 0.0 and variance > -EPSILON: variance = 0.0
    if variance < 0.0:
        raise Exception('ExamplesOpNoState: mean_and_sigma: negative variance')
    sigma = math.sqrt(variance)
    return sigma

def example_1():
    print "example_1"
    print "example functions from list to value: sum(), mean(), mean_and_sigma() "
    window_size = 2
    step_size = 2
    print "window_size = ", window_size
    print "step_size = ", step_size
    print ""

    x = Stream('x')
    # x is the in_stream.
    # sum() is the function on the window
    window_sum = window_op(sum, x, window_size, step_size)
    window_sum.set_name('sum')

    # mean() is the function on the window
    window_mean = window_op(mean, x, window_size, step_size)
    window_mean.set_name('mean')

    window_mean_and_sigma = \
       window_op(mean_and_sigma, x, window_size, step_size)
    window_mean_and_sigma.set_name('mean_and_sigma')


    x.extend([5, 11])
    print_streams_recent([x, window_sum, window_mean, window_mean_and_sigma])
    print""

    x.extend([9, 15, 19, 8, 20])
    print_streams_recent([x, window_sum, window_mean, window_mean_and_sigma])
    print""
    
    x.extend([19, 10, 11, 28, 30])
    print_streams_recent([x, window_sum, window_mean, window_mean_and_sigma])
    print""
    
   

def main():
    example_1()

if __name__ == '__main__':
    main()



