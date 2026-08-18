import time
import tracemalloc
import redis
from ratekeep.algorithms.fixed_window import FixedWindowLimiter
from limits.storage import RedisStorage
from limits.strategies import FixedWindowRateLimiter as LimitsFixedWindow
from limits import RateLimitItemPerMinute

r = redis.Redis(host='localhost', port=6379, db=0)

ratekeep_limiter = FixedWindowLimiter(r, 1000000, 60)

limits_storage = RedisStorage("redis://localhost:6379/0")
limits_strategy = LimitsFixedWindow(limits_storage)
limits_item = RateLimitItemPerMinute(1000000)

def test_ratekeep():
    ratekeep_limiter.is_allowed("bench_client")

def test_limits():
    limits_strategy.hit(limits_item, "bench_client")

def measure(name, func, iterations=15000):
    tracemalloc.start()
    latencies = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        latencies.append(time.perf_counter() - start)
        
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    latencies.sort()
    p99 = latencies[int(len(latencies) * 0.99)] * 1000
    throughput = iterations / sum(latencies)
    
    print(f"--- {name} ---")
    print(f"Throughput: {throughput:.2f} req/s")
    print(f"P99 Latency: {p99:.2f} ms")
    print(f"Memory Peak: {peak / 1024:.2f} KB\n")

if __name__ == "__main__":
    r.flushdb()
    measure("RateKeep (Lua Atomic)", test_ratekeep)
    
    r.flushdb()
    measure("Limits (Python standard)", test_limits)