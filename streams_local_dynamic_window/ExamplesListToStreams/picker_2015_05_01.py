if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from Stream import Stream, _no_value
from Operators import stream_func
import numpy as np
from functools import partial

"""
Constants
---------
LTA_SIZE: length of the base region in integers. This is a count
          and not in seconds.
STA_SIZE: length of the current region in integers. This is a count.
GAP_SIZE: length of gap between base and current region.
WINDOW_SIZE: length of the moving window.
STEP_SIZE: Number of values that the window is moved at each step.
MIN_GAP: Constant used in quenching successive picks. If a picks is
    sent to the hypocenter detector at time t, and another pick is
    detected at time t + delta, then the later pick is not sent to
    the hypocenter detector is delta < MIN_GAP.
EPSILON: Small number used to avoid division by 0.
LARGE_NUMBER: Value returned when dividing by values less
   than EPSILON.

"""

LTA_SIZE = 3
GAP_SIZE = 1
STA_SIZE = 3
WINDOW_SIZE = LTA_SIZE + GAP_SIZE + STA_SIZE
STEP_SIZE = 1
KSIGMA_THRESHOLD = 1.5
MIN_GAP = 1
EPSILON = 1e-10
LARGE_NUMBER = 1e10

def pick_window(list_t_and_3Dacc):
    """
    Parameters
    ---------
    list_t_and_3Dacc: list of 2-tuples where
         0-th element of tuple is the timestamp
         1-th element is a 3-tuple of accelerations
              in the directions:
              (north, east, vertical)

    Returns
    -------
    Returns a 2-element list: [horizontal_info, vertical_info]
    where horizontal_info are specified in the ksigma function
    below for the horizontal and vertical directions,
    i.e., a 4-tuple:
        (1) time of start of STA region,
        (2) max value in the STA region
        (3) number of standard deviations of mean of STA region
            above mean of LTA region, and
        (4) boolean indicating whether the number of standard
            deviations exceeds the threshold, KSIGMA_THRESHOLD.

    Variables
    ---------
    tstamps: 1D array of timestamps
    north, east, vertical: 1D array of accelerations
    horizontal: 1D array of accelerations

    """
    tstamps = np.array([v[0] for v in list_t_and_3Dacc])
    acc = [v[1] for v in list_t_and_3Dacc]
    north = np.array([a[0] for a in acc])
    east = np.array([a[1] for a in acc])
    horizontal = np.sqrt(north*north + east*east)
    vertical = np.array([a[2] for a in acc])


    def ksigma(t_and_acc):
        """
        Parameter
        ---------
        t_and_acc: 2_ tuple consisting of
           (i) array of times and
           (ii) array of accelerations
           The array of accelerations is 1-D. So, each
           direction --- horizontal, vertical --- is
           treated separately.

        Returns
        -------
        returns a 4-tuple:
        (0) time of start of STA region,
        (1) number of LTA standard deviations of mean of STA
            region above mean of LTA region, and
        (2) max value in the STA region
        (3) boolean indicating whether the number of standard
            deviations exceeds the threshold, KSIGMA_THRESHOLD.

        The order of the tuple, particularly the last two, is
        important for the quench function (below).

        """
        t, r = t_and_acc
        # t is a 1-D array of times
        # r is a 1-D array of values (e.g., accelerations)
        # r[:LTA_SIZE] is the subarray for the base case
        # r[-STA_SIZE:] is the subarray for the current point.
        # Division is by max(r[:LTA_SIZE].std(), EPSILON)) to
        # avoid division by 0.
        denominator = r[:LTA_SIZE].std()
        if denominator < EPSILON:
            sigma = LARGE_NUMBER
        else:
            sigma = (abs(r[:LTA_SIZE].mean() - r[-STA_SIZE:].mean())/
                     denominator)
        return (t[-STA_SIZE], sigma, max(r[-STA_SIZE:]),
                sigma > KSIGMA_THRESHOLD)

    return [ksigma((tstamps, horizontal)),
            ksigma((tstamps, vertical))
            ]



def quench(value_maxacc_bool, state):
    """
    Parameters
    ----------
    value_maxacc_bool: tuple of value, max_acc, boolean
       The boolean is True to indicate a pick.
         The boolean MUST be the last element of the tuple.
       max_acc is the max acceleration observed in the
          current window interval.
          max_acc MUST be the last-but-one element of
          the tuple
       The type of value is immaterial; value may be a tuple.
    state: The state of the stream is (gap, max_acc_observed)
       where:
         gap is the time since the last pick was registered.
         gap is initially set to MIN_GAP in the state of
         the quenched stream. For example, see h_quenched
         stream below.
         max_acc_observed is the maximum acceleration observed
         in the current quenching period. The difference
         between max_acc and max_acc_observed is that max_acc
         is the maximum acceleration in the current window,
         whereas max_acc_observed is the maximum acceleration
         over the current quenching window which may include
         multiple moving 'current' windows.

    Constants
    ---------
    _no_value: Imported from Stream. Used to indicate
         that there is no output. _no_value is used
         in place of Null.
    MIN_GAP: Only output True values for bool if gap
         is at least MIN_GAP.

    """
    gap, max_acc_observed = state
    # bool is the last element of value_maxacc_bool
    bool = value_maxacc_bool[-1]
    # The value returned discards the boolean
    return_value = value_maxacc_bool[:-1]
    # max_acc is the last_but_one element of value_maxacc_bool
    max_acc = value_maxacc_bool[-2]
    # The state of the stream is (gap, max_acc_observed)
    if gap < MIN_GAP:
        # This time point is within the quenching period.
        # So, output values only if the acceleration in
        # the current window exceeds the max acceleration
        # observed so far in this quenching period.
        gap += 1
        if max_acc <= max_acc_observed:
            state = (gap, max_acc_observed)
            # Return _no_value to indicate no pick.
            return (_no_value, state)
        else:
            max_acc_observed = max_acc
            state = (gap, max_acc_observed)
            return (return_value, state)
    elif not bool:
        # The actual time since the last value_maxacc_bool
        # was output is greater than or equal to MIN_GAP.
        # Since bool is False, do not return
        # value_maxacc_bool, and return _no_value instead.
        # Note: gap is not incremented because it is at
        # least MIN_GAP.
        return (_no_value, state)
    else:
        # The number of steps since the last output of
        # value_maxacc_bool is at least MIN_GAP. Since
        # bool is True, output return_value, and
        # reinitialize the state.
        gap = 0
        max_acc_observed = max_acc
        state = (gap, max_acc_observed)
        return (return_value, state)
    
"""
Function
--------
pick_h_and_v_in_stream

Input Streams
-------------
  Single input stream with elements of the form:
  (timestamp, [north_acc, east_acc, vertical_acc])
  where acc represents acceleration.

Output Streams
--------------
  Two output streams:
  (0): horizontal picks
  (1): vertical picks
  where a 'pick' is a 4-tuple:
        (1) time of start of STA region,
        (2) max value in the STA region
        (3) number of standard deviations of mean of STA region
            above mean of LTA region, and
        (4) boolean indicating whether the number of standard
            deviations exceeds the threshold, KSIGMA_THRESHOLD.



"""
pick_h_and_v_in_stream = \
  partial(stream_func, f_type='window', f=pick_window,
          num_outputs=2,  window_size=WINDOW_SIZE,
          step_size=STEP_SIZE)


"""
Function
--------
quench_stream

Input Streams
-------------
  Single input stream with elements of the form:
  (timestamp, value, boolean) where value is arbitrary
  and may be a tuple.

Output Streams
--------------
  Single output stream with elements of the form:
  (timestamp, value) where input elements where the
  boolean is True are passed to the output if the
  number of steps since the last output exceeds MIN_GAP.

state
-----
The state is a 2-tuple (gap, max_acc_observed)
where gap is the number of steps since quench_stream
last output a pick, and max_acc_observed is the
maximum acceleration observed in the quenching period.

Initially state is (MIN_GAP, 0.0) because the next
pick in the input stream must be sent to the output
stream (and hence gap=MIN_GAP initially), and the
maximum acceleration observed in this quenching period
is 0.0.
  
"""
quench_stream = partial(stream_func, f_type='element',
                        f=quench, num_outputs=1,
                        state=(MIN_GAP, 0.0))

    
def main():
    lst = [(0,[3, 4, 1]), (1, [4, 3, 2]), (2, [2, 2, 3]),
           (3, [1, 2, 1]), (4, [0, 0, 2]), (5, [1, 0, 1]),
           (6, [0, 1, 1]), (7, [2, 0, 1]), (8, [1.5, 2, 1]),
           (9, [2, 1.5, 3]), (10, [3, 4, 1]), (11, [4, 3, 0])
           ]
        
    x = Stream('x')
    h, v = pick_h_and_v_in_stream(x)
    h_quenched = quench_stream(h)
    v_quenched = quench_stream(v)
    
    h.set_name('h')
    v.set_name('v')
    h_quenched.set_name('h quenched')
    v_quenched.set_name('v quenched')
 
    x.extend(lst)
    x.print_recent()
    print
    h.print_recent()
    print
    v.print_recent()
    print
    h_quenched.print_recent()
    print
    v_quenched.print_recent()


if __name__ == '__main__':
    main()
