import time

def cpu_load_worker(target_percent):
    """
    Worker function that consumes a specific percentage of one CPU core.
    target_percent is a float between 0.0 and 100.0.
    Runs indefinitely until the process is terminated.
    """
    if target_percent <= 0.0:
        # If target is 0, just sleep indefinitely
        while True:
            time.sleep(1.0)

    # 100ms cycle time balance
    cycle_time = 0.1
    busy_time = cycle_time * (target_percent / 100.0)

    while True:
        cycle_start = time.perf_counter()
        # Run a busy loop for the active duration
        while (time.perf_counter() - cycle_start) < busy_time:
            pass
        # Sleep for the rest of the cycle
        elapsed = time.perf_counter() - cycle_start
        remaining = cycle_time - elapsed
        if remaining > 0:
            time.sleep(remaining)
