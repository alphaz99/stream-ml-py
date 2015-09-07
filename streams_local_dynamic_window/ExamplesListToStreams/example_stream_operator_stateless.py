"""This module contains examples of the stateless single stream source
"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Agent import *
from Stream import *
from Operators import stream_func


def main():
    def squares(input_list):
        return [v*v for v in input_list]
    def square(v):
        print 'v', v
        return v*v

    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

    stream_squares = partial(stream_func, 'list', squares)
    stream_square = partial(stream_func, 'element', square, num_outputs=1, state=None)

    import numpy as np
    y_stream = StreamArray('y stream')
    #z_stream = stream_operator(y_stream, f)
    z_stream = stream_func('list', squares, y_stream, 1)
    u_stream = stream_squares(y_stream)
    a = stream_square(y_stream)
    u_stream.set_name('u')
    a.set_name('a')
    z_stream.set_name('z')
    print_stream_recent(z_stream)
    print_stream_recent(u_stream)
    print_stream_recent(a)
    aray = np.asarray([3, 5])
    print 'aray', aray
    ## bray = aray + 2
    ## print 'bray', bray
    y_stream.extend(aray)
    print_stream_recent(z_stream)
    print_stream_recent(u_stream)
    print_stream_recent(a)
    y_stream.append(2)
    print_stream_recent(z_stream)
    print_stream_recent(u_stream)
    print_stream_recent(a)

if __name__ == '__main__':
    main()
