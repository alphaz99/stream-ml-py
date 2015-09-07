if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from scipy.signal import butter, lfilter
import numpy as np
import matplotlib.pyplot as plt
from Stream import Stream, _no_value
from Operators import stream_func
import SACreader

"""
Computes picks in a stream.

Run this as a script to see plots of the raw data,
filtered data, metrics, and ksigma values.

Or use the function pick_stream().

THE PYTHON SCRIPT
Call the Python script for this module with a single
parameter from the command line where the parameter is
the name of the SAC file.
For example:
python SACtoDataFile.py 20110111000000.2D.OBS26.SXZ.sac

1. The script echoes the name of the SAC file. For example:
SAC file: 20110111000000.2D.OBS26.SXZ.sac

2. Prints parameter values used in this run.

3. Plots raw data, filtered data, metrics, ksigma.

4. Prints picks, i.e., values sent for hypocenter calculation.


"""



"""
Constants
---------

Constants for the bandpass filter:
LOW_CUT: low cutoff frequency for the bandpass filter.
HIGH_CUT: high cutoff frequency for the bandpass filter.
FILTER_ORDER: order of the filter
FS: sample rate in Hz.


Constants for the metrics calculation:
METRICS_WINDOW_SIZE_IN_SECONDS
METRICS_STEP_SIZE_IN_SECONDS
A metric, such as standard deviation, is computed for
all the samples in a moving window. The number of
samples is METRICS_WINDOW_SIZE_IN_SECONDS * FS.

The metrics window is moved forward at each step by the step
size.

If a filter is applied that removes the DC (mean), then the
standard deviation metric is the same as root mean square.


Constants for ksigma calculation:
LTA_SIZE: length of the base region seconds
STA_SIZE: length of the current region in seconds
GAP_SIZE: length of gap between base and current region in seconds.
KSIGMA_THRESHOLD: unit-less nonnegative number.

ksigma is calculated for a window of size
WINDOW_SIZE = LTA_SIZE + GAP_SIZE + STA_SIZE
where all units are in seconds.
The window has WINDOW_SIZE elements. The first LTA_SIZE
elements of this window form the long-term average region,
and the last STA_SIZE elements form the short-term average
region.

For a window r, the LTA part (i.e., the region) is
       lta_part = r[:LTA_SIZE]
and the STA part is:
       sta_part = r[-STA_SIZE:]

ksigma is (sta_part.mean() - lta_part.mean())/
           lta_part.std()
       where std is standard deviation.

A 'pick' or anomaly is sent to the next stage of
computation (quench stream) only when ksigma exceeds
KSIGMA_THRESHOLD.

The sigma values are sent on a stream purely for the
purposes of plotting the values and debugging.

The ksigma window is moved forward by STA_SIZE at each
step.


Constants used in quenching picks.
MIN_GAP_IN_SECONDS: Time in seconds, used in quenching
    successive picks.

    A quenching period is started when a pick is sent
    to the hypocenter detector. The duration of the
    quenching period is MIN_GAP_IN_SECONDS.
    
    If a pick is  sent to the hypocenter detector at
    time t seconds, and another pick is detected at time
    t + delta seconds, then the later pick is NOT sent
    to the hypocenter detector if
              delta < MIN_GAP_IN_SECONDS
    and the pick's maximum acceleration is less than the
    max acceleration observed in this quenching period.
    If this pick's max acceleration exceeds the max value
    observed so far in this quenching period, then the
    pick is sent to the hypocenter detector even though
    the pick is in the quenching period.
    
EPSILON: Small number used to avoid division by 0.
LARGE_NUMBER: Value returned when dividing by values less
   than EPSILON.

"""
# Constants for the bandpass filter
LOWCUT = 0.1
HIGHCUT = 5.0
FILTER_ORDER = 5
FS = 50

# Constants for computing metrics
METRICS_WINDOW_SIZE_IN_SECONDS=1
METRICS_STEP_SIZE_IN_SECONDS=1
# We use window sizes in units of 1/FS time units in
# the calculations. For example, if FS = 50 Hz, then
# our calculations are in units of 1/50 = 20 milliseconds.
METRICS_WINDOW_SIZE = METRICS_WINDOW_SIZE_IN_SECONDS *FS
METRICS_STEP_SIZE = METRICS_STEP_SIZE_IN_SECONDS *FS

# Constants for computing ksigma
LTA_SIZE = 60 # in seconds
GAP_SIZE = 5  # in seconds
STA_SIZE = 1  # in seconds

# WINDOW_SIZE: length of the moving window for
# ksigma calculations.
WINDOW_SIZE = LTA_SIZE + GAP_SIZE + STA_SIZE
STEP_SIZE = STA_SIZE
KSIGMA_THRESHOLD = 6.0

# Constants for quenching.
MIN_GAP_IN_SECONDS=2
EPSILON = 1e-10
LARGE_NUMBER = 1e10
# MIN_GAP is in units of 1/FS seconds.
# MIN_GAP is used in calculations.
MIN_GAP = MIN_GAP_IN_SECONDS * FS


###########################################
# The picker.
###########################################
def pick_stream(stream):
    """ Returns picks (anomalies) in the raw stream.
    """
    stream_of_metrics = metrics_stream(filter_stream(stream))
    # ksigma_stream produces two output streams:
    # (0): stream of anomalies, i.e. stream of high sigma values
    # (1): stream of all sigma values. This is used only for
    #       plotting and debugging.
    stream_of_high_ksigmas, stream_of_ksigmas = \
      ksigma_stream(stream_of_metrics)
    return quench_stream(stream_of_high_ksigmas)

###########################################
# Read a SAC file and return a NumPy array
###########################################
def SAC_file_to_array(filename, decimate=1, skip=0, number=0):
    sac_file = SACreader.open_file(filename)
    location = [sac_file.get('stla'), sac_file.get('stlo')]
    delta = sac_file.get('delta')
    samples_per_second = int(1.0/delta + 0.5)
    print 'file name: ', filename
    print 'sensor location:', location
    return np.asarray(sac_file.data_points)

###########################################
# Bandpass filter
###########################################
def butter_bandpass(lowcut, highcut, fs, order):
    """ Returns parameters b, a for a Butterworth bandpass
    filter.
    b is the numerator array and a is the denominator array.
    The value returned for b is reversed because this
    simplifies the next step: filter_moving_window.
    
    Parameters
    -----------
    lowcut, highcut: low and high cutoff for the bandpass
            filter in Hertz.
    fs: the sampling rate in Hertz (number of samples/second)
    order: the order of the filter. Higher order gives sharper
        filters.

    """
    nyq = 0.5 * fs # The Nyquist frequency
    low = lowcut / nyq # Unit-less value for the cutoff.
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

bandpass_numerator, bandpass_denominator = \
  butter_bandpass(LOWCUT, HIGHCUT, FS, FILTER_ORDER)

  
def filter_moving_window(lst, state):
    """
    Parameters
    ----------
    lst: A list --- a window --- of (time, value)
         tuples, where the filter is applied to
         the sequence of values in successive
         windows.
    state: An array. The state of the filter.

    Returns
    -------
    ((t,output), state) where:
      output: scalar number
         The filtered value
      t: time
         time corresponding to the filtered value.
      state: 1D array
         The new state of the filter.
             
    Operation
    ---------
    From scipy.signal.lfilter notes, implement:
    a[0]*y[n] = b[0]*x[n] + b[1]*x[n-1] + ... + b[nb]*x[n-nb]
                        - a[1]*y[n-1] - ... - a[na]*y[n-na]
    where:
    arrays b, a are the numerator and denominator arrays for a linear
    filter.
    Note that the value returned for b by butter_bandpass is
    reversed, and this simplifies the calculation as seen below.
    x is the moving window input. The size of the window must be len(b).
    y is the state of the filter.

    """
    b, a = bandpass_numerator, bandpass_denominator
    # reverse bandpass_numerator (see filter_moving_window)
    b = b[::-1]

    if not a[0]:
        raise Exception()

    # lst is a list of 2-tuples (time value).
    t_and_x = np.array(lst)
    # x is a 1-D array of values
    x = t_and_x[:,1]
    # t is the time of the start of the window.
    # t is a scalar.
    t = t_and_x[0,0]
    # For the notes below, x[0] in our implementation is x[n-nb]
    # in scipy, .., and x[j] in our implementation is x[n-nb+j]
    # in scipy. This is because the sliding window has length nb
    # and the window sees x[n-nb,..., x]
 
    # From scipy.signal.lfilter notes:
    # a[0].y[n] = (b[0]*x[n] + b[1]*x[n-1] + ... + b[nb]*x[n-nb] -
    #         a[1]*y[n-1] + ... + a[na]*y[n-na])
    # So ensure:
    #       len(x) = len(b) = nb
    #       len(y) = len(a)-1 = na-1
    # The size of the moving window is nb and this ensures
    # len(x) == len(b)
    #
    # We store only y[n-1],... y[n-na] from the scipy notes, because
    # y[n] is computed at each step. Moreover, we reverse
    # y[n-1],...,y[n-na], i.e., y[0] in our implementation is y[n-1] in
    # the scipy notes, and y[na-1] in our implementation is y[n-na]
    # in the scipy notes.
    # So, a[1]*y[n-1] + ... + a[na]*y[n-na] in the scipy notes is
    # a[1]*y[0] +...+a[na]*y[na-1] in our notes,
    # i.e, it is sum(a[1:]*y).
    # Similarly, since we reversed b, b[0]...b[nb] in scipy is
    # b[nb],.., b[0] in our implementation, and since x[n-nb],..x[n]
    # in scipy is x[0], ..,x[nb] in our implementation:
    # b[0]*x[n] + b[1]*x[n-1] + ... + b[nb]*x[n-nb] in scipy is
    # sum(b*x)
    # y is the state of the filter.
     
    if np.isclose(a[0], 1.0):
        # This is the normal case.
        output = sum(b*x) - sum(a[1:]*state)
    else:
        output = (sum(b*x) - sum(a[1:]*state))/a[0]
    # Shift y to the right and add output as the leftmost element.
    state[1:] = state[:-1]
    state[0] = output
    return ((t,output), state)


def filter_stream(input_stream):
    """ Returns the filtered input stream.
    The filter is specified in function:
                   filter_moving_window

    """
    # The filter state is an array of length one less
    # than the length of bandpass_denominator.
    # Initialize the filter state to an arbitrary value,
    # here initialized to 0.0.
    # The initial elements of the filtered stream will be
    # noise because the initial state of the filter is
    # an array of zeros.
    filter_state = np.zeros(len(bandpass_denominator)-1)
    return stream_func(inputs=input_stream,
                       f_type='window',
                       f=filter_moving_window,
                       num_outputs=1,
                       state=filter_state,
                       window_size=len(bandpass_numerator),
                       step_size=1)


###########################################
# metrics
###########################################
def metrics(t_and_acc):
    t_and_acc = np.array(t_and_acc)
    t_window_start = t_and_acc[0,0]
    acc = t_and_acc[:,1]
    return (t_window_start, acc.std())

def metrics_stream(input_stream):
    return stream_func(inputs=input_stream,
                       f_type='window',
                       f=metrics,
                       num_outputs=1,
                       state=None,
                       window_size=METRICS_WINDOW_SIZE,
                       step_size=METRICS_STEP_SIZE)

###########################################
# ksigma calculation
###########################################
def ksigma_of_window(t_and_acc):
    """
    Parameter
    ---------
    t_and_acc: list of tuples (time, value)

    Returns
    -------
    (t, m) where t is the time at the
    start of an STA region and m is the maximum
    value in the STA region, for those regions where:
    (STA mean - LTA mean)/(LTA standard deviation)
    > KSIGMA_THRESHOLD

    If the LTA standard deviation is 0.0 (less than
    EPSILON), then the value returned is
    LARGE_VALUE to avoid division by 0.

    """
    t_and_acc = np.array(t_and_acc)
    r = t_and_acc[:,1]
    t = t_and_acc[-STA_SIZE, 0]
    # t is a 1-D array of times
    # r is a 1-D array of values (e.g., accelerations)
    # r[:LTA_SIZE] is the subarray for the base case
    # r[-STA_SIZE:] is the subarray for the current point.
    # Division is by max(r[:LTA_SIZE].std(), EPSILON)) to
    # avoid division by 0.
    lta_part = r[:LTA_SIZE]
    lta_part = lta_part[np.where(lta_part <
                                 np.percentile(lta_part, 80))[0]]
    sta_part = r[-STA_SIZE:]
    denominator = lta_part.std()
    if denominator < EPSILON:
        sigma = LARGE_NUMBER
    else:
        sigma = ((sta_part.mean() - lta_part.mean())/
                 denominator)
    if sigma <= KSIGMA_THRESHOLD:
        return [_no_value, (t, sigma)]
    else:
        return [(t, max(abs(sta_part))), (t, sigma)]


def ksigma_stream(input_stream):
    """ Returns a stream containing the
    (time, value) tuples for windows that
    exceed KSIGMA_THRESHOLD.
    
    Parameters
    __________
    input_stream: A stream of (time,value) tuples

    """
    return stream_func(inputs=input_stream,
                       f_type='window',
                       f=ksigma_of_window,
                       num_outputs=2,
                       state=None,
                       window_size=WINDOW_SIZE,
                       step_size=STEP_SIZE)

    

###########################################
# quenching
###########################################

def quench(t_and_acc, state):
    """
    Parameters
    ----------
    t_and_acc: tuple (time, value)
    state: The state of the stream is:
          t_quench_started, max_acc_in_quench_period
       where:
         t_quench_started is the time that this
         quenching period started.
         max_acc_in_quench_period is the maximum
         acceleration observed so far in this quenching
         period.

    Constants
    ---------
    _no_value: Imported from Stream. Used to indicate
         that there is no output. _no_value is used
         in place of Null.
    MIN_GAP: number in units of time.
         The first pick starts a quenching interval
         with a duration of MIN_GAP time units. If
         a pick occurs during a quenching interval
         then the pick is discarded if the magnitude
         of the pick is less than or equal to the
         maximum magnitude observed so far in this
         quenching period; if the magnitude of this
         pick is higher than those observed so far,
         this higher-magnitude pick is output.

    """
    t_quench_started, max_acc_in_quench_period = state
    t, acc = t_and_acc
    ## print 'state', state
    ## print 't_and_acc', t_and_acc
    if t - t_quench_started <= MIN_GAP:
        # Time t is within the quenching period.
        # So, output values only if the acceleration in
        # the current window exceeds the max acceleration
        # observed so far in this quenching period.
        if acc <= max_acc_in_quench_period:
            # state doesn't change.
            # Return _no_value to indicate no pick.
            return (_no_value, state)
        else:
            # max acc in window exceeds max acceleration
            # observed in this quenching period.
            max_acc_in_quench_period = acc
            state = (t_quench_started, max_acc_in_quench_period)
            return ((t, max_acc_in_quench_period), state)
    else:
        # Time t is outside the quenching period.
        # So, start a new quenching period starting
        # at time t, and with maximum acceleration observed
        # of acc.
        # state = (t, acc) = t_and_acc
        return (t_and_acc, t_and_acc)


def quench_stream(stream):
    """
    Input Streams
    -------------
      Single input stream with elements of the form:
      (timestamp, value) where value is a number.

    Output Streams
    --------------
      Single output stream with elements of the form:
      (timestamp, value).
      A (time, value) element in the input stream is
      put in the output stream if the time is outside
      a quenching interval or if the value is greater
      than the maximum value observed in this quenching
      interval.

    state
    -----
    The state is a 2-tuple:
    (t_quench_started, max_acc_in_quench_period)
    see function quench.

    Initially state is (-(MIN_GAP+1), 0.0) because the
    next pick must start a new quenching period even
    if the pick is at time 0.
  
"""
    return stream_func(inputs=stream,
                       f_type='element',
                       f=quench,
                       num_outputs=1,
                       state=(MIN_GAP, 0.0))



def main(SAC_filename):

    # This script is for reading a SAC file.
    # If you use an npy file, do the following
    # filename = '20110111000000.2D.OBS34.SXZ.npy'
    # Or load data_array from a stored .npy file
    # data_array = np.load(filename)

    data_array = SAC_file_to_array(SAC_filename)
    print 'length of raw data array', len(data_array)

    # stream_length should be len(data_array);
    # however, for debugging we may want to
    # run shorter streams.
    stream_length = int(len(data_array)/30)
    # data_array is made shorter, if necessary,
    # for debugging.
    print 'length of data array used in this run: ', stream_length    
    data_array = data_array[:stream_length]

    # Since, the SAC files do not have time stamps
    # we create time stamps. Here t is a stream of
    # time stamps in increasing order 0, 1, 2...
    # for each value in the input array.
    stream_of_times = Stream('Stream of Times')
    # Create the stream of raw data
    stream_of_raw_data = Stream('Stream of Raw Data')
    # Create timed_raw_data_stream which is a
    # stream of tuples (t, data_array[t]).
    # All succeeding streams will be of this
    # tuple form: (time, value at time).
    def identity_function(a):
            return a
    stream_of_timed_raw_data = stream_func(
        inputs=[stream_of_times, stream_of_raw_data],
        f_type='element',
        f=identity_function,
        num_outputs=1)

    ## # THE SCRIPT WITHOUT PLOTS: THE BASIC PICKER
    ## # You can run the entire picker without plots
    ## # as shown next. Or you can run the script with
    ## # plots.
    ## stream_of_picks = pick_stream(
    ##     stream_of_timed_raw_data)

    ## # Populate the stream of raw data.
    ## stream_of_raw_data.extend(data_array)
    ## # Populate the stream of times.
    ## stream_of_times.extend(range(stream_length))

    ## print
    ## print 'picks sent to next step: hypocenter calculation'
    ## print 'time : magnitude of acceleration'
    ## for v in stream_of_picks.recent[:stream_of_picks.stop]:
    ##     print '{0:.1f} : {1:.2f}'.format(v[0]/50.0, v[1])
    ## return
    ## # FINISHED SCRIPT FOR BASIC PICKER WITHOUT PLOTS.

    
    # THE SCRIPT WITH PLOTS
    # Create the network of streams.
    stream_of_filtered_values = filter_stream(
        stream_of_timed_raw_data)
    stream_of_metrics = metrics_stream(
        stream_of_filtered_values)
    stream_of_high_ksigmas, stream_of_ksigmas = \
      ksigma_stream(stream_of_metrics)
    stream_of_picks = quench_stream(stream_of_high_ksigmas)

    # Populate the stream of raw data.
    stream_of_raw_data.extend(data_array)
    # Populate the stream of times.
    stream_of_times.extend(range(stream_length))

    # Print parameter values
    print
    print 'Parameters for bandpass filter:'
    print 'LOWCUT = {0}. HIGHCUT = {1}'.format(LOWCUT, HIGHCUT)
    print
    print 'Parameters for metrics computation:'
    print 'METRICS_WINDOW_SIZE_IN_SECONDS = {0}, METRICS_STEP_SIZE_IN_SECONDS = {1}'.format(
        METRICS_WINDOW_SIZE_IN_SECONDS, METRICS_STEP_SIZE_IN_SECONDS)
    print
    print 'Parameters for ksigma calculation in seconds:'
    print 'LTA_SIZE={0}, GAP_SIZE={1}, STA_SIZE={2}'.format(
        LTA_SIZE, GAP_SIZE, STA_SIZE)
    print 'KSIGMA_THRESHOLD={0}'.format(KSIGMA_THRESHOLD)
    print
    print 'Parameters for Quenching:'
    print 'MIN_GAP_IN_SECONDS={0}'.format(MIN_GAP_IN_SECONDS)
    print

    # Plots
    plt.plot(data_array)
    plt.title('raw data')
    plt.show()
    plt.close()

    # filtered_values strips the time part of the (time, value)
    # tuple. This is because we only want to plot values and
    # we don't want to plot time.
    # The most recent values in a stream s are in an array:
    #       s.recent[:s.stop]
    # So, the most recent values of stream_of_filtered_values is:
    # stream_of_filtered_values.recent[:stream_of_filtered_values.stop]
    filtered_values = \
      [v[1] for v in
       stream_of_filtered_values.recent[:stream_of_filtered_values.stop]]
    # We don't plot the first 5000 values because the filter doesn't get
    # initialized until at least 5000 values have passed through the filter.
    # Future: Initialize filter constants better. Currently they are set to
    # 0.
    plt.plot(filtered_values[5000:])
    plt.title('filtered data')
    plt.show()
    plt.close()

    # metrics_values strips the time component of the (time,value)
    # tuple.
    metrics_time_and_values = \
      stream_of_metrics.recent[:stream_of_metrics.stop]
    metrics_values = [v[1] for v in  metrics_time_and_values]
    # The first 100 values are garbage because the first 5000 values
    # of the filter are garbage.
    plt.plot(metrics_values[100:])
    plt.title('metrics')
    plt.show()
    plt.close()

    ksigma_time_and_values = \
      stream_of_ksigmas.recent[:stream_of_ksigmas.stop]
    ksigma_values = [v[1] for v in  ksigma_time_and_values]
    plt.plot(ksigma_values)
    plt.title('ksigma')
    plt.show()
    plt.close()

    print
    print 'picks sent to next step: hypocenter calculation'
    print 'time in seconds : magnitude of acceleration'
    for v in stream_of_picks.recent[:stream_of_picks.stop]:
        print '{0:.1f} : {1:.2f}'.format(v[0]/50.0, v[1])

if __name__ == '__main__':
    main(sys.argv[1])
