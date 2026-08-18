import threading
import redis
from ratekeep.algorithms.fixed_window import FixedWindowLimiter

def test_fixed_window_concurrency():
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.flushdb()
    
    limiter = FixedWindowLimiter(r, limit=50, window_size=60)
    client_id = "test_concurrent_user"
    
    success_count = 0
    lock = threading.Lock()
    
    def make_request():
        nonlocal success_count
        if limiter.is_allowed(client_id):
            with lock:
                success_count += 1

    threads = []
    for _ in range(100):
        t = threading.Thread(target=make_request)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    assert success_count == 50