from time import time
from unittest import TestCase, main

from counter import Counter


MILLION = 1_000_000


class TestCounter(TestCase):
    def setUp(self) -> None:
        self.current_sec = 0
        self.counter = Counter(timestamp_func=self.time)

    def time(self):
        """Fake time function, to enable time passage testing"""
        return self.current_sec

    def tick(self, seconds=1.0):
        """Move the fake time forward."""
        self.current_sec += seconds

    def test_initial_zero(self):
        """No events, count should be zero."""
        self.assertEqual(self.counter.get_count(1), 0)

    def test_zero_timewindow(self):
        """Empty time window should contain zero events."""
        self.counter.on_event()
        # Important: time has to have progressed, otherwise, the "zero time" window includes the last event.
        self.tick()
        self.assertEqual(self.counter.get_count(0), 0)

    def test_one(self):
        """In the simplest use case, expect the single event to count."""
        self.counter.on_event()
        self.assertEqual(self.counter.get_count(1), 1)

    def test_count(self):
        """Expect the counter to return the count for the right time window only"""
        for i in range(100):
            self.counter.on_event()
            self.tick()
        self.tick(.1)
        # We are at 100.1 seconds, and we have 100 events, spaced out by 1-second intervals.
        # The most recent event was 1.1 seconds ago.
        # If we ask for events of the last 10 seconds, we should get 9.
        self.assertEqual(self.counter.get_count(10), 9)

    def test_expire_immediately(self):
        """Given a cleaning_threshold of zero, the expired events should be cleaned up immediately."""
        self.counter.cleaning_threshold = 0  # This will force the counter to clean up old events right away
        TIME_STEP = 50

        # Events up to the default 300 sec increase the count - that's 3 events
        for i in range(3):
            self.counter.on_event()
            self.tick(TIME_STEP)
            self.assertEqual(self.counter.get_count(MILLION), i + 1)
            self.tick(TIME_STEP)

        # Now the old events should begin to get pruned, but the insertion happens first
        # So the stable number gets bumped to 4.
        for i in range(100):
            self.counter.on_event()
            self.tick(TIME_STEP)
            self.assertEqual(self.counter.get_count(MILLION), 4)
            self.tick(TIME_STEP)

    def test_nonzero_threshold(self):
        """Expect the counter to prune old events once in every X events."""
        self.counter.cleaning_threshold = 100  # Clean up after adding 100 new events
        TIME_STEP = 400  # One tick, and all events are too old.
        for i in range(100):
            self.counter.on_event()
            self.tick(TIME_STEP)
            self.assertEqual(self.counter.get_count(MILLION), i + 1)
            self.tick(TIME_STEP)

        for i in range(100):
            self.counter.on_event()  # First iteration here should trigger the cleanup. Subsequent 100 should not.
            self.tick(TIME_STEP)
            self.assertEqual(self.counter.get_count(MILLION), i + 1)
            self.tick(TIME_STEP)

    def test_indistinguishable_times(self):
        """Events that occur too close in time should still be counted distinctly."""
        # Make first 100 events happen at the same time
        for i in range(100):
            self.counter.on_event()
        self.tick()
        for i in range(100):
            self.counter.on_event()
        self.assertEqual(self.counter.get_count(MILLION), 200)

    def test_stress(self):
        """
        Expect to handle a large number of events per second.

        NOTE: this test uses default time() function, and takes at least 100 msec.
        """
        counter = Counter()  # Using all default parameters.
        start = time()
        while time() - start < .1:
            for i in range(10000):
                counter.on_event()
        print('Registered %s events in %0.3f msec' % (counter.get_count(MILLION), (time() - start) * 1000))
        self.assertGreater(counter.get_count(MILLION), 100)  # The test might run on a slow machine.


if __name__ == '__main__':
    main()
