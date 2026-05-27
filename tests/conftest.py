import pytest
import redis

@pytest.fixture(autouse=True)
def flush_redis():
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.flushdb()
    yield
    r.flushdb()