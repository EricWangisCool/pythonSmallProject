import multiprocessing
import os
import atexit
import logging
from .cpu_worker import cpu_load_worker

try:
    import psutil
except ImportError:
    psutil = None

# Initialize psutil CPU percent tracking
if psutil is not None:
    psutil.cpu_percent(interval=None)

class CPUManager:
    def __init__(self):
        self.processes = []
        self.target_percentage = 0
        # Register exit handler to terminate subprocesses when the app closes
        atexit.register(self.stop_all)

    def start_load(self, target_percent):
        """
        Starts CPU worker processes to target target_percent total system CPU increase.
        target_percent is between 0 and 100.
        """
        # Ensure target_percent is valid
        target_percent = max(0, min(100, int(target_percent)))
        
        # Stop existing processes first
        self.stop_all()
        
        self.target_percentage = target_percent
        if target_percent == 0:
            return
            
        num_cores = os.cpu_count() or 1
        # Total load needed across all cores (system percentage * number of cores)
        total_load = target_percent * num_cores
        
        # Calculate how many processes we need to spawn
        # Each process can consume up to 100% of a core.
        remaining_load = total_load
        
        logging.info(f"Starting CPU load: target={target_percent}%, total_load={total_load}% over {num_cores} cores")
        
        try:
            while remaining_load > 0:
                proc_load = min(remaining_load, 100.0)
                remaining_load -= proc_load
                
                # Start a separate process to bypass the Python GIL
                p = multiprocessing.Process(
                    target=cpu_load_worker,
                    args=(proc_load,)
                )
                p.daemon = True
                p.start()
                self.processes.append(p)
        except Exception as e:
            logging.error(f"Failed to spawn CPU loader process: {e}")
            self.stop_all()
            raise

    def stop_all(self):
        """Terminates all running CPU worker processes."""
        if self.processes:
            logging.info(f"Stopping all {len(self.processes)} CPU loader processes")
            for p in self.processes:
                try:
                    if p.is_alive():
                        p.terminate()
                        p.join(timeout=0.2)
                except Exception as e:
                    logging.error(f"Error terminating CPU loader process: {e}")
            self.processes = []
        self.target_percentage = 0

    def get_status(self):
        """Returns the status of the CPU manager and system CPU usage."""
        active_processes = [p for p in self.processes if p.is_alive()]
        active_count = len(active_processes)
        
        # Get real-time system CPU usage
        system_cpu = 0.0
        if psutil is not None:
            # Use 0.1s interval to get accurate readings across different Flask worker threads
            system_cpu = psutil.cpu_percent(interval=0.1)
            
        num_cores = os.cpu_count() or 1
        
        return {
            "running": self.target_percentage > 0 and active_count > 0,
            "target_percentage": self.target_percentage,
            "process_count": active_count,
            "num_cores": num_cores,
            "system_cpu": system_cpu,
            "psutil_available": psutil is not None
        }

# Singleton instance
cpu_manager = CPUManager()
