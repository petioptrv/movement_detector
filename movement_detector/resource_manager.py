from queue import Queue
import time
from threading import Thread

from movement_detector.settings import SystemSettings


class ResourceManager(Thread):
    def __init__(self, job_queue: Queue, settings: SystemSettings = None):
        Thread.__init__(self, target=self._loop)
        if settings is None:
            self._settings = SystemSettings()
        else:
            self._settings = settings
        self._job_queue = job_queue

    def _loop(self):
        while True:
            job = self._job_queue.get()
            if job is None:
                time.sleep(1)
            else:
                func, args, kwargs = job
                if kwargs is None:
                    kwargs = {}
                ret = func(*args, **kwargs)
                if ret is not None:
                    break

    @staticmethod
    def stop():
        return True
