# Vlad's Sample Code For Huckleberry Onsite

These samples demonstrate code in Python. There are two sample modules:
`counter` and `elevator`. The counter module implements a class that could be used
for something like counting page loads, for example, for the purposes of 
site rate limiting. The elevator module contains logic for determining the next stop
of an elevator, based on current position, movement, and pressed buttons.

These examples were written as exercises for recent job interviews. (The slight 
differences in coding style between the two modules are due to the varying requirements 
from the respective tasks.) Although this 
is not actual production code, it was written to approximate  
production quality. Specifically, the comments, the documentation, and the unit tests
were written at a level that I consider appropriate in a production system.

## Running tests

To run all tests, please run from the current directory:
```shell script
python -m unittest discover test
```

To run tests for a particular module, please run from current directory:
```shell script
PYTHONPATH=`pwd` python test/test_counter.py
PYTHONPATH=`pwd` python test/test_elevator.py
```

## Event Counter 


### Counter class

`Counter` allows the user to count event occurrences, and query their number over a time window.

The max age of events, the timestamp function, and the cleanup threshold can be parametrized (see `__init__`).


#### Constructor
```python
counter = Counter(max_seconds, timestamp_func, cleaning_threshold)
```

##### Parameters
 - `max_seconds`: The number of seconds we remember an event. Default value is 300 sec (5 minutes).
 - `timestamp_func`: The function used to get current timestamp, in seconds.
    Default value is the built-in `time.time`. This is useful for two purposes:
    * for substituting high-precision timer function instead of the default one
    * for unit tests, to simulate time passage.
        
 - `cleaning_threshold`: How many new events should we accept before we attempt to prune the expired ones? 
 Default value is 100,000. This parameter allows us to tune the 
 trade-off between memory cleanup and performance.

#### on_event

```python
counter.on_event()
```

Registers an event. 
Calling this function will cause a current timestamp to be added 
to the list of events. It may or may not trigger pruning of expired events, depending on the cleaning threshold.

#### get_count
```python
number_of_events_in_the_last_second = counter.get_count(1)
```
Returns the number of events registered over the previous number of `seconds`.
Note that the old events may have been pruned earlier, and then the count will not include them.

##### Parameters
 - `seconds`: The time window, in seconds, over which to count the events.
 
### Performance considerations

 - Pre-allocation of memory seems like a good idea, but it would have a limited effect in this implementation.
   Performance measurements have shown that pre-allocating timestamp lists, or using pre-allocated
   numpy arrays, speeds things up by a few percents, not enough to justify the additional code complexity.
   However, in a C/C++ implementation, one could greatly benefit from pre-allocating memory,
   since array/vector element access would be nearly instantaneous.
   
   For example, a C++ implementation could maintain a collection of pre-allocated timestamp arrays,
   treating them like memory pages, and keep track of current position with an iterator member variable.
   The "memory pages" could be added when we reached capacity (e.g. during a rapid-fire series of calls to `on_event()`),
   but during normal operation, no memory allocation/deallocation would be necessary.
   
 - Pruning of the old events, which involves a binary search over the event collection,
   can and should be optimized. This is what the `cleaning_threshold` parameter is for.
   Performance tests vary from machine to machine, but typically,
   having `cleaning_threshold` of `1` allows us to process roughly 2-3 times as many events per second
   as with `cleaning_threshold` set to `0`, and the performance gains continue up to about 100,000, with diminishing
   effect. 1K-event threshold appears to be almost an order of magnitude faster than zero-event threshold, but threshold of 100K is only
   a few percents faster than 1K. Use a larger value if you have plenty of memory and 
   want to squeeze another little bit of performance in Python.
   To measure the effect of the `cleaning_threshold` value on performance, 
   the following example code could be used:

```python

test_event_count = 1_000_000
for i in range(5):
    for threshold in (0, 1, 2, 100, 1000, 100_000, 2_000_0000):
        c = Counter(max_seconds=1, cleaning_threshold=threshold)
        start = time()
        for i in range(test_event_count):
            c.on_event()
        delta_sec = time() - start
        print('cleanup: skip every {:,} events: {:,.0f} events/sec'.format(threshold, (test_event_count / delta_sec)))
```

Example output:
```text
cleanup: skip every 0 events: 193,196 events/sec
cleanup: skip every 1 events: 449,283 events/sec
cleanup: skip every 2 events: 483,657 events/sec
cleanup: skip every 100 events: 1,459,107 events/sec
cleanup: skip every 1,000 events: 1,543,472 events/sec
cleanup: skip every 100,000 events: 1,572,990 events/sec
cleanup: skip every 20,000,000 events: 1,554,175 events/sec
```

--------

## Elevator: the nextFloor() Function

The function `nextFloor()` computes the next floor the elevator will stop on, given
the current floor, current direction, and the current set of pressed buttons.

Example usage:

```python
nextFloor(42, UP, ['43U', '55D', '2I'])

# will return: 43
```

### Parameters
 - `currentFloor`: What floor we are passing at the moment?
 - `currentDirection`: Are we going UP or DOWN at the moment?
 - `buttonsPressed`: Which buttons have been pressed?

If there are no buttons pressed, `nextFloor` will return current floor.

The `buttonsPressed` is a list of elements, which are 
encoded in the format: `<floor number> + <command>`, 
where `<command>` is one of `U` (up), `D` (down), or `I` ("inside", for buttons inside the elevator). 

If there is no floor in the direction of the current movement of the elevator,
a `RuntimeError` is raised.
 
Please see the unit tests in `test/test_elevator.py` for more usage examples.

### Helper Functions

#### parseButtonCommand(command, currentFloor, currentDirection)
 Given an elevator button, along with current floor and direction,
 return tuple `(floor, direction)`.

 For example:
    
  - '5U' -> (5, `UP`)
  - '9I' -> (9, `<direction>`)

 In the last example, the <direction> is determined based on current
 floor and direction of the elevator — if we are moving towards the 9th floor,
 the answer will be `currentDirection`, otherwise the opposite direction.

#### isApproaching(targetFloor, currentFloor, currentDirection)
Are we approaching the target floor, given our present location and direction?
