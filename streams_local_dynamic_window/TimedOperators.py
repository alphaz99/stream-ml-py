from Agent import *
from Stream import *
from MergeSplitOpStructures import *

def list_index_for_timestamp(in_list, start_index, timestamp):
    """ A helper function for timed operators.

    Returns positive integer i where:
    either: 'FOUND TIME WINDOW IN IN_LIST'
        i > start_index and
        i <= in_list.stop  and
        in_list.list[i-1].time >= timestamp and
        (i == start_index+1 or in_list.list[i-2].time < timestamp)
    or: 'NO TIME WINDOW IN IN_LIST'
        i < 0 and
           (in_list.list[in_list.stop-1] <= timestamp
                       or
           (in_list.start = in_list.stop)

    Requires:
         start_index >= in_list.start and
         start_index < in_list.stop

    """
    if in_list.start == in_list.stop: return -1

    if start_index < in_list.start or start_index >= in_list.stop:
        raise Exception('start_index out of range: start_index =', start_index,
                        ' in_list.start = ', in_list.start,
                        ' in_list.stop = ', in_list.stop)
    for i in range(start_index, in_list.stop):
        # assert i <= in_list.stop-1
        if in_list.list[i].time >= timestamp:
            return i
    # assert in_list.list[in_list.stop - 1] < timestamp
    return -1


def timed_many_to_many(f, in_streams, num_out_streams, window_size, step_size,
                       state=None):
    range_out = range((num_out_streams))
    range_in = range(len(in_streams))
    window_start_time = 0
    combined_state = (window_start_time, state)

    def transition(in_lists, combined_state):
        window_start_time, state = combined_state
        output_lists = [ [] for _ in range_out]
        window_end_time = window_start_time + window_size
        window_start_indexes = [ in_lists[j].start for j in range_in]
        while True:
            window_end_indexes = [list_index_for_timestamp(
                in_lists[j],
                window_start_indexes[j],
                window_end_time) for j in range_in]
            if any(window_end_indexes[j] < 0 for j in range_in):
                break
            windows = [in_lists[j].list[window_start_indexes[j]: \
                                       window_end_indexes[j]] for j in range_in]
            increments = f(windows) if state is None else f(windows, state)

            for k in range_out:
                output_lists[k].append(TimeAndValue(window_end_time, increments[k]))
            window_start_time += step_size
            window_end_time += step_size
            new_window_start_indexes = [list_index_for_timestamp(
                in_lists[j],
                window_start_indexes[j],
                window_start_time) for j in range_in]
            if any(new_window_start_indexes[j] < 0 for j in range_in):
                break
            ## #CHECKING FOR PROGRESS TOWARDS TERMINATION
            ## if (any(new_window_start_indexes[j] < window_start_indexes[j]
            ##        for j in range_in) or
            ##        all(new_window_start_indexes[j] == window_start_indexes[j]
            ##        for j in range_in)):
            ##     raise Exception('TimedOperator: start_indexes')
            window_start_indexes = new_window_start_indexes

        combined_state = (window_start_time, state)
        return (output_lists, combined_state, window_start_indexes)
    # Create agent
    out_streams = [Stream() for v in range(num_out_streams)]
    combined_state = (window_start_time, state)
    Agent(in_streams, out_streams, transition, combined_state)

    return out_streams

def timed_merge(f, in_streams, window_size, step_size, state=None):
    return merge_structure(timed_many_to_many, f, in_streams,
                           window_size, step_size, state=None)

def timed_split(f, in_stream, num_out_streams, window_size, step_size,
                state=None):
    return split_structure(timed_many_to_many, f, in_stream, num_out_streams,
                           window_size, step_size, state=None)

def timed_op(f, in_stream, window_size, step_size, state=None):
    return op_structure(timed_many_to_many, f, in_stream, window_size,
                        step_size, state=None)

