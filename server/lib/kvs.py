import os
from redis import StrictRedis

kvs = StrictRedis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))
