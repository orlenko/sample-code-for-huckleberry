from time import time
from bisect import bisect_left


class Counter:
    """Counter allows the user to count event occurrences, and query their number over a time window.

    The max age of events, the timestamp function, and the cleanup threshold can be parametrized (see `__init__`).
    """
    def __init__(self, max_seconds=300.0, timestamp_func=None, cleaning_threshold=100_000):
        """
        :param max_seconds: The number of seconds we remember an event. Default is 300 sec (5 minutes).
        :param timestamp_func: The function used to get current timestamp, in seconds.
            Default is the built-in time.time().
        :param cleaning_threshold: How many new events should we accept before we attempt to prune the expired ones?
            Default value is 100,000.
        """
        self.max_seconds = max_seconds
        self.timestamp_func = timestamp_func or time
        self.cleaning_threshold = cleaning_threshold
        self.timestamps = []  # Collection of the event timestamps.
        self.last_clean_count = 0  # Last-known event count (see `prune_old_timestamps`).

    def on_event(self):
        """Register an event.
        Calling this function will cause a current timestamp to be added to the list of events.
        It may or may not trigger pruning of expired events.
        """
        self.timestamps.append(self.timestamp_func())
        should_prune = self.cleaning_threshold < len(self.timestamps) - self.last_clean_count
        if should_prune:
            self.prune_old_timestamps()

    def get_count(self, seconds):
        """Get the number of events registered over the previous `seconds`.
        Note that the old events may have been pruned earlier, and then the count will not include them.

        :param seconds: The time window, in seconds, over which to count the events.
        :return: Count of events since `seconds` ago, or the full count of available events, whichever is smaller.
        """
        since = self.timestamp_func() - seconds
        return len(self.timestamps) - bisect_left(self.timestamps, since)

    def prune_old_timestamps(self):
        """Remove events that are too old, based on the `max_seconds` parameter (see __init__).

        This method is called automatically from `on_event()`, based on the `cleaning_threshold` value.
        """
        too_old = self.timestamp_func() - self.max_seconds
        i = bisect_left(self.timestamps, too_old)
        if i:
            self.timestamps = self.timestamps[i:]
        self.last_clean_count = len(self.timestamps)
