import threading

class Lock:
    """Wrapper for threading.Lock so it can be used in with"""
    def __init__(self):
        self._lock = threading.Lock()

    def __enter__(self):
        if self._lock.acquire():
            return self._lock
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()
        return True
