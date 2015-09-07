from Agent import *
from Stream import *
from MergeSplitOpStructures import *

def window_many_to_many(f, in_streams, num_out_streams, window_size, step_size, state=None):
    def transition(in_lists, state=None):
        range_out = range((num_out_streams))
        range_in = range(len(in_streams))
        output_lists = [ [] for _ in range_out ]
        window_starts = [in_list.start for in_list in in_lists]

        smallest_list_length = min(v.stop - v.start for v in in_lists)
        if window_size > smallest_list_length:
            #in_lists_start_values = [in_list.start for in_list in in_lists]
            return (output_lists, state, [in_list.start for in_list in in_lists])

        num_steps = 1 + (smallest_list_length - window_size)/step_size
        for i in range(num_steps):
            windows = [in_lists[j].list[window_starts[j]:window_starts[j]+window_size] \
                       for j in range_in]
            increments = f(windows) if state is None else f(windows, state)
            for k in range_out: output_lists[k].append(increments[k])
            window_starts = map(lambda v: v+step_size, window_starts)

        in_lists_start_values = [in_list.start + num_steps*step_size for in_list in in_lists]
        return (output_lists, state, in_lists_start_values)

    # Create agent
    out_streams = [Stream() for v in range(num_out_streams)]
    Agent(in_streams, out_streams, transition, state)

    return out_streams

    
def window_merge(f, in_streams, window_size, step_size, state=None):
    return merge_structure(window_many_to_many, f, in_streams,
                           window_size, step_size, state=None)

def window_split(f, in_stream, num_out_streams,
                 window_size, step_size, state=None):
    return split_structure(window_many_to_many, f, in_stream, num_out_streams,
                           window_size, step_size, state=None)

def window_op(f, in_stream, window_size, step_size, state=None):
    return op_structure(window_many_to_many, f, in_stream,
                        window_size, step_size, state=None)
