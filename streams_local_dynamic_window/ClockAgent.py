from Stream import *
from PrintFunctions import *
import sched
import time

scheduler = sched.scheduler(time.time, time.sleep)

def clock_stream(period, num_periods, name='clock_stream'):
    clock_stream = Stream(name)
    period_number = 0
    def tick(period_number):
        clock_stream.append(time.time())
        period_number += 1
        if period_number < num_periods:
            scheduler.enter(period, 1, tick, (period_number,))
    scheduler.enter(period, 1, tick, (period_number,))
    return clock_stream
def example():
    x = clock_stream(0.25, 2)
    print_stream(x)
def main():
    ## print_stream(clock_stream(0.25, 2))
    example()
    scheduler.run()
if __name__ == '__main__':
    main()
        
        
