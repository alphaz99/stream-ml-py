if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ClockAgent import clock_stream, scheduler
from PrintFunctions import print_stream, print_stream_with_index

def stream_from_list(trigger_stream, list_of_values, step_size=1):
    # state is the number of values output so far
    state = 0
    def transition(in_lists, state):
        new_state = state+step_size
        if len(list_of_values) > new_state:
            output_list = list_of_values[state:new_state]
        else:
            output_list = []
            print "StreamOutputWhenCalled.stream_from_list. Finished streaming list."
        state = new_state
        # in_lists_start_values = []
        # return(output_lists, state, in_lists_start_values)
        return ([output_list], state, [])
    # Create agent
    out_stream = Stream()
    # in_streams = []
    # call_streams = [trigger_stream]
    # Agent(in_streams, out_streams, transition, state, call_streams)
    Agent([], [out_stream], transition, state, [trigger_stream])

    return out_stream

def stream_from_file(trigger_stream, file_name, step_size=1):
    with open(file_name, "r") as f:
            list_of_values = map(lambda x: float(x), f.read().split())
    return stream_from_list(trigger_stream, list_of_values, step_size)


def main():
    file_name = 'ExampleFile.dat'
    trigger_stream = clock_stream(period=0.1,
                                  num_periods=10,
                                  name='trigger_stream')
    s = stream_from_file(trigger_stream, file_name, step_size=1)
    s.set_name('s')
    print_stream_with_index(s)

    scheduler.run()

if __name__ == '__main__':
    main()
    
