from gevent import Greenlet, sleep as gsleep
from gevent.queue import Queue, Empty as EmptyError


from utils.log_helpers import logging
logger = logging.getLogger(__name__)


class Worker(Greenlet):
    def __init__(self, w, q, *args, **kwargs):
        self.work = w
        self.queue = q
        self.args = args
        self.kwargs = kwargs
        self.running = False

        super(Worker, self).__init__()

    def get_queue(self):
        return self.queue

    def add_work(self, work):
        self.queue.put(work)

    def stop(self):
        self.running = False

    def run(self):
        self.running = True

        while self.running:
            try:
                work = self.queue.get_nowait()
            except EmptyError as ee:
                pass
            else:
                self.work(work)
            gsleep(0)

        logger.warn('Worker exiting')


def get_queue_worker(w, *args, **kwargs):
    q = Queue()
    w = Worker(w, q, *args, **kwargs)
    return q, w
