from Stream import *
from ListOperators import *

def print_stream(s):
    def print_list(lst):
        for v in lst: print s.name, ' = ', v
        return []
    op(print_list, s)

def print_stream_with_index(s):
    state=0
    def print_list_with_index(lst, state):
        for v in lst:
            print '{stream_name} [ {index} ] = {value}'.format(
                stream_name=s.name, index=state, value=v)
            state += 1
        return ([], state)
    op(print_list_with_index, s, state)

def print_stream_indexes_where_threshold_is_exceeded(s,
                                                     THRESHOLD,
                                                     starting_index=0,
                                                     SUPPRESSION_LENGTH=0,
                                                     index_of_last_anomaly=0):
    current_index = starting_index
    state = (current_index, index_of_last_anomaly,)
    def print_list_indexes_where_threshold_is_exceeded(lst, state):
        current_index, index_of_last_anomaly = state
        for v in lst:
            if v > THRESHOLD:
                if current_index > index_of_last_anomaly + SUPPRESSION_LENGTH:
                    index_of_last_anomaly = current_index
                    print '{stream_name} [ {index} ] = {value:.2f}'.format(
                        stream_name=s.name, index=current_index, value=v)
            current_index += 1
            state = (current_index, index_of_last_anomaly,)
        return ([], state)
    op(print_list_indexes_where_threshold_is_exceeded, s, state)
            

def print_stream_recent(s):
    print s.name, " = ", s.recent[:s.stop]

def print_streams_recent(lst_of_s):
    for s in lst_of_s:
        print s.name, " = ", s.recent[:s.stop]


def print_streams_recent_TimeAndValue(list_of_streams_of_TimeAndValue):
    for s in list_of_streams_of_TimeAndValue:
        print " \n "
        print s.name + '______________________________'
        print " "
        for t_and_v in s.recent[:s.stop]:
            next_item =  "(" + str(t_and_v.time) + ", " + str(t_and_v.value) + ")"
            print next_item,
