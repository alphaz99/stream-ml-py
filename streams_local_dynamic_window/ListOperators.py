if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *

def many_to_many(f, in_streams, num_out_streams,
                 state=None, call_streams=None):
    def transition(in_lists, state=None):
        smallest_list_length = min(v.stop - v.start for v in in_lists)
        input_lists = [v.list[v.start:v.start+smallest_list_length] for v in in_lists]
        # Carry out the state-transition operation which 
        # (1) updates state and (2) computes the output list for 
        # the single output stream of this agent.
        # func returns a list and has the side effect of modifying
        # state
        if state is None:
            output_lists = f(input_lists)
        else:
            output_lists, state = f(input_lists, state)
        in_lists_start_values = [v.start+smallest_list_length for v in in_lists]
        return (output_lists, state, in_lists_start_values)

    # Create agent
    out_streams = [Stream() for v in range(num_out_streams)]
    Agent(in_streams, out_streams, transition, state, call_streams)

    return out_streams

def merge(f, in_streams, state=None, call_streams=None):
    def transition(in_lists, state=None):
        smallest_list_length = min(v.stop - v.start for v in in_lists)
        input_lists = [v.list[v.start:v.start+smallest_list_length] for v in in_lists]
        if state is None:
            output_list = f(input_lists)
        else:
            output_list, state = f(input_lists, state)
        in_lists_start_values = [v.start+smallest_list_length for v in in_lists]
        return ([output_list], state, in_lists_start_values)
    # Create agent
    out_stream = Stream()
    Agent(in_streams, [out_stream], transition, state, call_streams)
    return out_stream


def split(f, in_stream, num_out_streams=2, state=None, call_streams=None):
    def transition(in_lists, state=None):
        in_list = in_lists[0]
        if state is None:
            output_lists = f(in_list.list[in_list.start:in_list.stop])
        else:
            output_lists, state = \
              f(in_list.list[in_list.start:in_list.stop], state)
        return (output_lists, state, [in_list.stop])
    # Create agent
    out_streams = [Stream() for v in range(num_out_streams)]
    Agent([in_stream],                 # list of input streams
          out_streams,
          transition,
          state, call_streams)

    return out_streams
        

def op(f, in_stream, state=None, call_streams=None):
    def transition(in_lists, state=None):
        in_list = in_lists[0]
        if state is None:
            output_list = f(in_list.list[in_list.start:in_list.stop])
        else:
            output_list, state = \
              f(in_list.list[in_list.start:in_list.stop], state)
        return ([output_list], state, [in_list.stop])

    # Create agent
    out_stream = Stream()
    Agent([in_stream], [out_stream], transition, state, call_streams)

    return out_stream
