import os

import redis
from rq import Worker, Queue, Connection

LISTEN = ['high', 'default', 'low']

REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

REDIS_CONN = redis.from_url(REDIS_URL)

if __name__ == '__main__':
  with Connection(REDIS_CONN):
    worker = Worker(map(Queue, LISTEN))
    worker.work()

# $eof
