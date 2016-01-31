from gevent.queue import Queue as gQueue

import logging as _logging
import json
import inspect
import os


class QueueLogger(_logging.StreamHandler):

    DEFAULT_FORMAT = "%(name)-12s: %(levelname)-8s %(message)-4s"

    def __init__(self, emitter=None, fmt=None, max_queue=50):
        super(QueueLogger, self).__init__()
        self.emitter = emitter or gQueue(max_queue)
        self.set_format(fmt or self.DEFAULT_FORMAT)

    def get_emitter(self):
        return self.emitter

    def emit(self, record):
        # print dir(record)
        # for r in dir(record):
        #     print r, getattr(record, r)
        print 'putting log message in queue'
        record = self.formatter.format(record)
        if self.emitter.full():
            print 'message not delivered:', self.emitter.get()
        self.emitter.put(record)

    def set_format(self, fmt):
        self.setFormatter(_logging.Formatter(fmt))

setattr(_logging, 'QueueLogger', QueueLogger)

PATH = '{0}/{1}'.format(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), 'config.json')

conf = json.loads(open(PATH).read())
basic_config = conf.pop('basicConfig')
basic_config['level'] = getattr(_logging, basic_config['level'], _logging.DEBUG)

_logging.basicConfig(**basic_config)

formatter = None
for handler_conf in conf.pop('handlers'):
    handler = getattr(_logging, handler_conf['type'], None)()
    handler.setLevel(getattr(_logging, handler_conf['level'], _logging.DEBUG))

    formatter = _logging.Formatter(getattr(handler_conf, 'formatter', basic_config['format']))
    handler.setFormatter(formatter)
    _logging.getLogger('').addHandler(handler)


def get_ws_log_queue():
    for handler in _logging.getLogger('').handlers:
        if isinstance(handler, QueueLogger):
            return handler.emitter

logging = _logging

logging.getLogger(__name__).warn('unused config: %s' % conf) if conf else None

