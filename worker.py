import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

myHostname = "se-project.redis.cache.windows.net"
myPassword = "+K1w7moukZgDPg3uG2AynrVC3tcAThAULppTUZdCmd0="

# redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.StrictRedis(host=myHostname, port=6380,
                      password=myPassword, ssl=True)
# conn = redis.from_url("plagiarism-checker.redis.cache.windows.net")

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
