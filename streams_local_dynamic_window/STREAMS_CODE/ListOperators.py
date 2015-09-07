if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *

# ASSERTIONS USED IN FILE
def assert_is_list_of_streams_or_None(x):
    assert isinstance(x, list) or isinstance(x, tuple) or x is None,\
      'Expected {0} to be None or list or tuple.'.format(x)
    if x is not None:
        assert all(isinstance(l, Stream) for l in x),\
          'Expected {0} to be a list (or tuple) of streams.'.format(x)

def assert_is_list_of_streams(x):
    assert isinstance(x, list) or isinstance(x, tuple),\
      'Expected {0} to be a list or tuple'.format(x)
    assert all(isinstance(l, Stream) for l in x),\
      'Expected {0} to be a list (or tuple) of streams'.format(x)

def assert_is_list_of_lists(x, list_size=None):
    assert isinstance(x, list) or isinstance(x, tuple),\
      'Expected {0} to be a list or tuple'.format(x)
    assert all(isinstance(l, list) for l in x),\
      'Expected {0} to be a list (or tuple) of lists'.format(x)
    assert list_size is None or list_size == len(x), \
      'Expected len({0}) == {1}, or {1} to be None'.format(x, list_size)
    
def assert_is_list_or_None(x):
    assert isinstance(x, list) or x is None, \
      'Expected {0} to be a list or None'.format(x)

def assert_is_list(x):
    assert isinstance(x, list), \
      'Expected {0} to be a list'.format(x)


      
# STREAM FUNCTION DEFINITIONS.
# Each of the functions below creates an agent for a specific
# input-output condition: 0, 1, or more than 1 inputs, and
# 0, 1 or more than 1 outputs.
# A source has 0 inputs and 1 or more outputs.
# A sink has 0 outputs and 1 or inputs.
# merge has more than 1 input and 1 output.
# split has 1 input and more than 1 output.
# A stream operator has 1 input and 1 output.
# many_to_many has more than 1 input and more than 1 output.

# The function is either stateless or stateful.
# A stateful function has a state which is updated each
# time the function is executed.

# Each of the functions below create a stream function
# from list_func, a function on lists. The signature of
# list_func is specified in the function comments, e.g.,
# list_func: () -> list for a function that has no inputs
# and that returns a list.

# The functions have an argument call_streams which is
# a list of streams. The function is executed when a
# stream in call_streams is extended. If call_streams
# is None, then the function (by means of its Agent)
# sets call_streams to inputs, and in this case the
# function is executed when any of its input streams is
# extended.

# The function may have num_outputs as an argument.
# If num_outputs is 0, the function does not return a
# stream; if it is 1 it returns a single stream, and if
# it is more than 1 it returns a list of streams where
# the size of the list is num_outputs.

# The structure of each of these functions is as follows:
# (1) specify the signature of list_func, e.g.
#      list_func: list -> list

# (2) check on the type of call_streams (either list of
#     streams or None). The check is of the form:
#     assert_is_list_of_streams(call_streams) or
#     assert_is_list_of_streams_or_None(call_streams)

# (3) DEFINE STATE TRANSITION FOR THE AGENT
#     def transition(in_lists, state):
#     Where in_lists is a list of type InList.
#     InList = namedtuple('InList', ['list', 'start', 'stop'])
#     for a variable inlist of type InList:
#     inlist.list[inlist.start:inlist.stop] is an ordinary list
#     which is the list that the function has access to.

#     First extract a list or list of lists on which the
#     function operates.
#     If the function has a single input stream, then it operates
#     on a single inlist from which it extracts the ordinary list
#     input_list as follows:
#     input_list = in_list.list[in_list.start:in_list.stop]

#     If the function has more than one input stream, then the
#     function operates on a list of lists, all of the same size.
#     This list of lists is called input_lists and is obtained
#     as follows:
#     smallest_list_length = min(v.stop - v.start for v in in_lists)
#     input_lists = \
#       [v.list[v.start:v.start+smallest_list_length] for v in in_lists]
#
# (4) EXECUTE list_func: THE FUNCTION ON LISTS THAT IS LIFTED TO
#     A FUNCTION ON STREAMS

#     Execute list_func on the list or list of lists extracted in (3).
#         Execute either list_func(arg) or
#                        output = list_func(args)
#         where the output and args depend on the function.

#     The args may have a state, and may have either a list or a
#     list of lists. And the function may return a state and may
#     also return either a list or a list of lists.

#     STATELESS AND STATEFUL list_func(args)
#     For stateful functions, the args and the output include state.
#     For stateless functions, the args and output don't include state.

#     RETURN VALUES for list_func:
#     If the function has:
#       (i) no output streams, then the function does not return a value.
#       (ii) one output stream return a list, and
#       (iii) more than one output stream return a list of lists.

#     NUMBER OF INPUT STREAMS for list_func:
#     If the function has:
#     (i) no input stream (i.e., it is a source) then args of list_func do 
#         not include a list or a list of lists.
#     (ii) a single input stream, then the args of list_func include a
#          single list.
#     (iii) more than one input stream, then the args of list_func include
#           a list of lists.

# (5) check the type of the output of list_func, e.g.
#     assert_is_list(output_list)

# (6) return (output_lists, state, in_lists_start_values)
#      where:
#       output_lists is a list of lists.
#       state is an arbitrary object (almost always not None)
#      in_lists_start_values is a list of pointers
#      to the input stream, pointing to the value that will be 
#      read in the stream in the NEXT execution of the function.
#     
# (7) Create output streams (if any) of the function and
#     create an agent to update the output and execute the
#     function when values are appened to any stream in call_streams.
#     If the function has:
#     (i) no output streams, then the function returns [],
#     (ii) a single output stream then return a single stream.
#     (iii) more than one output stream then return a list of streams.
      

def single_output_source_stateless(list_func, call_streams):
    # list_func:  () -> list
    assert_is_list_of_streams(call_streams)
    
    def transition(in_lists, state):
        output_list = list_func()
        assert_is_list(output_list)
        return ([output_list], state, [0])

    # Create agent
    output_stream = Stream()
    input_stream = Stream()
    state=None
    Agent([input_stream], [output_stream], transition, state, call_streams)
    return output_stream


def single_output_source_stateful(list_func, state, call_streams):
    # list_func: state -> list, state
    assert_is_list_of_streams(call_streams)

    def transition(in_lists, state):
        output_list, state = list_func(state)
        assert_is_list(output_list)
        return ([output_list], state, [0])

    # Create agent
    output_stream = Stream()
    input_stream = Stream()
    Agent([input_stream], [output_stream], transition, state, call_streams)
    return output_stream


def many_outputs_source_stateless(list_func, num_outputs, call_streams):
    # list_func:  () -> list of lists.
    assert_is_list_of_streams(call_streams)

    def transition(in_lists, state):
        output_lists = list_func()
        assert_is_list_of_lists(output_lists, list_size=num_outputs)
        return (output_lists, state, [0])

    # Create agent
    output_streams = [Stream() for i in range(num_outputs)]
    input_stream = Stream()
    state = None
    Agent([input_stream], output_streams, transition, state, call_streams)
    return output_streams


def many_outputs_source_stateful(list_func, num_outputs, state, call_streams):
    # list_func:  state -> list of lists, state.
    assert_is_list_of_streams(call_streams)
    
    def transition(in_lists, state):
        output_lists, state = list_func(state)
        assert_is_list_of_lists(output_lists, list_size=num_outputs)
        return (output_lists, state, [0])

    # Create agent
    output_streams = [Stream() for i in range(num_outputs)]
    input_stream = Stream()
    Agent([input_stream], output_streams, transition, state, call_streams)
    return output_streams


def single_input_sink_stateless(list_func, input_stream, call_streams=None):
    # list_func: list  -> None
    assert_is_list_of_streams_or_None(call_streams)
    def transition(in_lists, state):
        in_list = in_lists[0]
        input_list = in_list.list[in_list.start:in_list.stop]
        list_func(input_list)
        # Since this function has no output stream, set the output_list
        # to be anything, e.g., [].
        return ([], state, [in_list.stop])

    # Create agent
    output_streams = []
    state = None
    Agent([input_stream], output_streams, transition, state, call_streams)
    return output_streams



def single_input_sink_stateful(list_func, input_stream, state, call_streams=None):
    # list_func:   list, state -> state
    assert_is_list_of_streams_or_None(call_streams)

    def transition(in_lists, state):
        # see single_input_sink_stateless
        in_list = in_lists[0]
        input_list = in_list.list[in_list.start:in_list.stop]
        state = list_func(input_list, state)
        return ([], state, [in_list.stop])

    # Create agent
    output_streams = []
    Agent([input_stream], output_streams, transition, state, call_streams)
    return output_streams


def stream_operator_stateless(list_func, input_stream, call_streams=None):
    # list_func:    list -> list
    assert_is_list_of_streams_or_None(call_streams)

    def transition(in_lists, state):
        in_list = in_lists[0]
        input_list = in_list.list[in_list.start:in_list.stop]
        output_list = list_func(input_list)
        assert_is_list(output_list)
        return ([output_list], state, [in_list.stop])

    # Create agent
    output_stream = Stream()
    state = None
    Agent([input_stream], [output_stream], transition, state, call_streams)
    return output_stream


def stream_operator_stateful(list_func, input_stream, state, call_streams=None):
    # list_func:   list, state -> list, state
    assert_is_list_of_streams_or_None(call_streams)

    def transition(in_lists, state):
        in_list = in_lists[0]
        input_list = in_list.list[in_list.start:in_list.stop]
        output_list, state = list_func(input_list, state)
        assert_is_list(output_list)
        assert state is not None, 'stateful operator did not return state'
        return ([output_list], state, [in_list.stop])

    # Create agent
    output_stream = Stream()
    Agent([input_stream], [output_stream], transition, state, call_streams)
    return output_stream


def split_stateless(list_func, input_stream, num_outputs, call_streams=None):
    # list_func: list -> list_of_lists
    #                where len(list_of_lists) == num_outputs
    assert_is_list_of_streams_or_None(call_streams)
    def transition(in_lists, state):
        in_list = in_lists[0]
        input_list = in_list.list[in_list.start:in_list.stop]
        output_lists = list_func(input_list)
        assert_is_list_of_lists(output_lists, num_outputs)
        return (output_lists, state, [in_list.stop])

    # Create agent
    output_streams = [Stream() for i in range(num_outputs)]
    state = None
    Agent([input_stream], output_streams, transition, state, call_streams)
    return output_streams


def split_stateful(list_func, input_stream, num_outputs, state, call_streams=None):
    # list_func: list, state -> list_of_lists, state
    #                where len(list_of_lists) == num_outputs
    assert_is_list_of_streams_or_None(call_streams)
    def transition(in_lists, state):
        in_list = in_lists[0]
        input_list = in_list.list[in_list.start:in_list.stop]
        output_lists, state = list_func(input_list, state)
        assert_is_list_of_lists(output_lists, num_outputs)
        return (output_lists, state, [in_list.stop])

    # Create agent
    output_streams = [Stream() for i in range(num_outputs)]
    Agent([input_stream], output_streams, transition, state, call_streams)
    return output_streams


def many_inputs_sink_stateless(list_func, inputs, call_streams=None):
    # list_func: list_of_lists -> empty
    assert_is_list_of_streams_or_None(call_streams)
    
    def transition(in_lists, state):
        smallest_list_length = min(v.stop - v.start for v in in_lists)
        input_lists = [v.list[v.start:v.start+smallest_list_length] for v in in_lists]
        list_func(input_lists)
        output_lists = []
        in_lists_start_values = [v.start+smallest_list_length for v in in_lists]
        return (output_lists, state, in_lists_start_values)

    # Create agent
    output_streams = []
    state = None
    Agent(inputs, output_streams, transition, state, call_streams)
    return output_streams


def many_inputs_sink_stateful(list_func, inputs, state, call_streams=None):
    # list_func: list_of_lists -> state
    assert_is_list_of_streams_or_None(call_streams)

    def transition(in_lists, state):
        smallest_list_length = min(v.stop - v.start for v in in_lists)
        input_lists = [v.list[v.start:v.start+smallest_list_length] for v in in_lists]
        state = list_func(input_lists, state)
        output_lists = []
        in_lists_start_values = [v.start+smallest_list_length for v in in_lists]
        return (output_lists, state, in_lists_start_values)

    # Create agent
    output_streams = []
    Agent(inputs, output_streams, transition, state, call_streams)
    return output_streams


def merge_stateless(list_func, inputs, call_streams=None):
    # list_func: list_of_lists -> list
    assert_is_list_of_streams_or_None(call_streams)

    def transition(in_lists, state):
        smallest_list_length = min(v.stop - v.start for v in in_lists)
        input_lists = [v.list[v.start:v.start+smallest_list_length] for v in in_lists]
        output_list = list_func(input_lists)
        assert_is_list(output_list)
        in_lists_start_values = [v.start+smallest_list_length for v in in_lists]
        return ([output_list], state, in_lists_start_values)

    # Create agent
    output_stream = Stream()
    state = None
    Agent(inputs, [output_stream], transition, state, call_streams)
    return output_stream


def merge_stateful(list_func, inputs, state, call_streams=None):
    # list_func: list_of_lists, state -> list, state
    assert_is_list_of_streams_or_None(call_streams)

    def transition(in_lists, state):
        smallest_list_length = min(v.stop - v.start for v in in_lists)
        input_lists = [v.list[v.start:v.start+smallest_list_length] for v in in_lists]
        output_list, state = list_func(input_lists, state)
        assert_is_list(output_list)
        smallest_list_length = min(v.stop - v.start for v in in_lists)        
        in_lists_start_values = [v.start+smallest_list_length for v in in_lists]
        return ([output_list], state, in_lists_start_values)

    # Create agent
    output_stream = Stream()
    Agent(inputs, [output_stream], transition, state, call_streams)
    return output_stream


def many_to_many_stateless(list_func, inputs, num_outputs, call_streams=None):
    # list_func: list of lists -> list of lists
    assert_is_list_of_streams_or_None(call_streams)

    def transition(in_lists, state):
        smallest_list_length = min(v.stop - v.start for v in in_lists)
        input_lists = [v.list[v.start:v.start+smallest_list_length] for v in in_lists]
        output_lists = list_func(input_lists)
        assert_is_list_of_lists(output_lists, num_outputs)
        in_lists_start_values = [v.start+smallest_list_length for v in in_lists]
        return (output_lists, state, in_lists_start_values)

    # Create agent
    output_streams = [Stream() for i in range(num_outputs)]
    state = None
    Agent(inputs, output_streams, transition, state, call_streams)
    return output_streams
    


def many_to_many_stateful(list_func, inputs, num_outputs, state, call_streams=None):
    # list_func: list of lists, state -> list of lists, state
    assert_is_list_of_streams_or_None(call_streams)

    def transition(in_lists, state):
        smallest_list_length = min(v.stop - v.start for v in in_lists)
        input_lists = [v.list[v.start:v.start+smallest_list_length] for v in in_lists]
        output_lists, state = list_func(input_lists, state)
        assert_is_list_of_lists(output_lists, num_outputs)
        in_lists_start_values = [v.start+smallest_list_length for v in in_lists]
        return (output_lists, state, in_lists_start_values)

    # Create agent
    output_streams = [Stream() for i in range(num_outputs)]
    Agent(inputs, output_streams, transition, state, call_streams)
    return output_streams


def stream_func(list_func, inputs, num_outputs, state=None, call_streams=None):
    #inputs is one of the following:
    # None, a Stream, or a list of Streams

    # num_outputs is a nonnegative integer;
    # it is the number of output streams of
    # this function

    # call_streams is a list of Streams

    # state is None or is an arbitrary objects

    # list_func returns a list of num_outputs list
    # and may, in addition, return a state.
    # The arguments of list_func are:
    #     empty if inputs is None
    #     a list if inputs is a Stream
    #     a list of lists if inputs is a list of Streams

    # Check types of parameters
    if not isinstance(num_outputs, int):
        raise TypeError('Expected num_outputs to be int, not:',
                        num_outputs)
    if num_outputs < 0:
        raise ValueError('Expected num_outputs to be nonnegative, not:',
                         num_outputs)
    
    if not((inputs is None) or
           (isinstance(inputs, Stream) or
           ((isinstance(inputs, list) and
             (all(isinstance(l, Stream) for l in inputs))
             )
           ))):
        raise TypeError('Expected inputs to be None, Stream or list of Streams, not:',
                        inputs)

    if not((call_streams is None) or
           ((isinstance(call_streams, list) and
             (all(isinstance(l, Stream) for l in call_streams))
             )
           )):
        raise TypeError('Expected call_streams to be None, Stream or list of Streams, not:',
                        call_streams)

    if inputs is None:
        # Check that call_streams is nonempty
        if len(call_streams) < 1:
            raise TypeError('Expected call_streams to be a nonempty list of streams, not:',
                        call_streams)
    
        if num_outputs == 0:
            raise TypeError('inputs is None and num_outputs == 0')
        elif num_outputs == 1:
            if state is None:
                return single_output_source_stateless(
                    list_func, call_streams)
            else:
                return single_output_source_stateful(
                    list_func, state, call_streams)
        else:
            if state is None:
                return many_outputs_source_stateless(
                    list_func, num_outputs, call_streams)
            else:
                return many_outputs_source_stateful(
                    list_func, num_outputs, state, call_streams)

    elif isinstance(inputs, Stream):
        input_stream = inputs
        if num_outputs == 0:
            if state is None:
                return single_input_sink_stateless(
                    list_func, input_stream, call_streams)
            else:
                return single_input_sink_stateful(
                    list_func, input_stream, state, call_streams)
        elif num_outputs == 1:
            if state is None:
                return stream_operator_stateless(
                    list_func, input_stream, call_streams)
            else:
                return stream_operator_stateful(
                    list_func, input_stream, state, call_streams)
        else:
            if state is None:
                return split_stateless(
                    list_func, input_stream, num_outputs, call_streams)
            else:
                return split_stateful(
                    list_func, input_stream, num_outputs, state, call_streams)

    else:
        if num_outputs == 0:
            if state is None:
                return many_inputs_sink_stateless(
                    list_func, inputs, call_streams)
            else:
                return many_inputs_sink_stateful(
                    list_func, inputs, state, call_streams)
        elif num_outputs == 1:
            if state is None:
                return merge_stateless(
                    list_func, inputs, call_streams)
            else:
                return merge_stateful(
                    list_func, inputs, state, call_streams)
        else:
            if state is None:
                return many_to_many_stateless(
                    list_func, inputs, num_outputs, call_streams)
            else:
                return many_to_many_stateful(
                    list_func, inputs, num_outputs, state, call_streams)



def main():
    x_list = [3, 4, 5, 2, 9, 11, 15, 10, 19, 2, 4, 7, 6, 17, 10, 12]
    xx_list = range(10, 20, 1)
    def f():
        import random
        return [random.random()]
    def ff():
        return xx_list
    def g(state):
        return (x_list[state: state+2], state+2)
    def h():
        return ([x_list[0:3], x_list[3:6]])
    def p(state):
        return([x_list[state:state+2], x_list[state+2:state+4]], state+4)
    def q(input_list):
        print "single input sink, stateless:", input_list
        return
    def r(input_list, state):
        output_list = input_list
        for i in range(len(input_list)):
            state += input_list[i]
            output_list[i] = state
        print 'single input sink, stateful:', output_list
        return state
    def s(input_list):
        return [2*v for v in input_list]
    def t(input_list, state):
        output_list = input_list
        for i in range(len(input_list)):
            state += 2 * input_list[i]
            output_list[i] = state
        return (output_list, state)
    def u(input_list):
        output_0_list = filter(lambda v: v%2 == 0, input_list)
        output_1_list = filter(lambda v: v%2 != 0, input_list)
        output_lists = [output_0_list, output_1_list]
        return output_lists
        
    def v(input_list, state):
        output_0_list = filter(lambda v: v%2 == 0, input_list)
        output_1_list = filter(lambda v: v%2 != 0, input_list)
        output_0_list = map(lambda v: state*v, output_0_list)
        output_1_list = map(lambda v: state*v, output_1_list)
        state += 1
        output_lists = [output_0_list, output_1_list]
        return (output_lists, state)
    
    def w(list_of_lists):
        a = list_of_lists[0]
        b = list_of_lists[1]
        print "many input sink, stateless:",\
          [x+y for x,y in zip(a, b)]


    def gg(list_of_lists, state):
        print "state", state
        a = list_of_lists[0]
        b = list_of_lists[1]
        result_list = [0] * min(len(a), len(b))
        for i in range(len(result_list)):
            state += a[i] + b[i]
            result_list[i] = state
        print "many input sink, stateful:", result_list
        return state

    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

        
    trigger = Stream()
    x_stream = stream_func(f, inputs=None, num_outputs=1, state=None, call_streams=[trigger])
    xx_stream = stream_func(ff, inputs=None, num_outputs=1, state=None, call_streams=[trigger])    
    y_stream = stream_func(g, inputs=None, num_outputs=1, state=0, call_streams=[trigger])
    a_stream, b_stream = stream_func(h, inputs=None, num_outputs=2, state=None, call_streams=[trigger])
    c_stream, d_stream = stream_func(p, inputs=None, num_outputs=2, state=0, call_streams=[trigger])
    stream_func(q, inputs=c_stream, num_outputs=0, state=None, call_streams=[trigger])
    stream_func(r, inputs=c_stream, num_outputs=0, state=0, call_streams=[trigger])
    e_stream = stream_func(s, inputs=c_stream, num_outputs=1, state=None, call_streams=[trigger])
    aa_stream = stream_func(list_func=t, inputs=c_stream, num_outputs=1, state=0, call_streams=[trigger])
    bb_stream, cc_stream = \
      stream_func(list_func=u, inputs=x_stream, num_outputs=2, state=None, call_streams=[trigger])
    dd_stream, ee_stream = \
      stream_func(list_func=v, inputs=x_stream, num_outputs=2, state=0, call_streams=[trigger])
    stream_func(w, inputs=[x_stream, xx_stream], num_outputs=0, state=None, call_streams=[trigger])
    stream_func(gg, inputs=[x_stream, xx_stream], num_outputs=0, state=0, call_streams=[trigger])
    x_stream.set_name('x_stream')
    xx_stream.set_name('xx_stream')
    y_stream.set_name('y_stream')
    a_stream.set_name('a_stream')
    b_stream.set_name('b_stream')
    c_stream.set_name('c_stream')
    d_stream.set_name('d_stream')
    e_stream.set_name('e_stream')
    aa_stream.set_name('aa_stream')
    bb_stream.set_name('bb_stream')
    cc_stream.set_name('cc_stream')
    dd_stream.set_name('dd_stream')
    ee_stream.set_name('ee_stream')

    print_stream_recent(x_stream)
    print_stream_recent(xx_stream)
    print_stream_recent(y_stream)
    print_stream_recent(a_stream)
    print_stream_recent(b_stream)
    print_stream_recent(c_stream)
    print_stream_recent(d_stream)
    print_stream_recent(e_stream)
    print_stream_recent(aa_stream)
    print_stream_recent(bb_stream)
    print_stream_recent(cc_stream)
    print_stream_recent(dd_stream)
    print_stream_recent(ee_stream)
    
    trigger.extend([1])
    print_stream_recent(x_stream)
    print_stream_recent(xx_stream)
    print_stream_recent(y_stream)
    print_stream_recent(a_stream)
    print_stream_recent(b_stream)
    print_stream_recent(c_stream)
    print_stream_recent(d_stream)
    print_stream_recent(e_stream)
    print_stream_recent(aa_stream)
    print_stream_recent(bb_stream)
    print_stream_recent(cc_stream)
    print_stream_recent(dd_stream)
    print_stream_recent(ee_stream)

    trigger.extend([1])
    print_stream_recent(x_stream)
    print_stream_recent(xx_stream)
    print_stream_recent(y_stream)
    print_stream_recent(a_stream)
    print_stream_recent(b_stream)
    print_stream_recent(c_stream)
    print_stream_recent(d_stream)
    print_stream_recent(e_stream)
    print_stream_recent(aa_stream)
    print_stream_recent(bb_stream)
    print_stream_recent(cc_stream)
    print_stream_recent(dd_stream)
    print_stream_recent(ee_stream)

    trigger.extend([1])
    print_stream_recent(e_stream)
    print_stream_recent(aa_stream)
    print_stream_recent(bb_stream)
    print_stream_recent(cc_stream)
    print_stream_recent(dd_stream)
    print_stream_recent(ee_stream)

if __name__ == '__main__':
    main()
