import time
import math
from typing import List, Tuple

class AdaptiveAnalyzer:
    def __init__(self, redis_client, history_window: int = 60, z_score_threshold: float = 2.5):
        self.redis = redis_client
        self.history_window = history_window
        self.z_score_threshold = z_score_threshold

    def _get_inter_arrival_times(self, timestamps: List[float]) -> List[float]:
        if len(timestamps) < 2:
            return []
        return [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]

    def _calculate_stats(self, values: List[float]) -> Tuple[float, float]:
        if not values:
            return 0.0, 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)
        return mean, std_dev

    def analyze_and_adjust(self, client_id: str, base_limit: int) -> int:
        now = time.time()
        key = f"rate_limit:history:{client_id}"
        
        pipeline = self.redis.pipeline()
        pipeline.zremrangebyscore(key, 0, now - self.history_window)
        pipeline.zadd(key, {str(now): now})
        pipeline.zrange(key, 0, -1, withscores=True)
        pipeline.expire(key, self.history_window)
        results = pipeline.execute()
        
        timestamps = [score for _, score in results[2]]
        
        if len(timestamps) < 10:
            return base_limit
            
        intervals = self._get_inter_arrival_times(timestamps)
        mean, std_dev = self._calculate_stats(intervals)
        
        if std_dev == 0:
            return max(1, int(base_limit * 0.1))
            
        current_interval = timestamps[-1] - timestamps[-2] if len(timestamps) >= 2 else 0
        z_score = abs(current_interval - mean) / std_dev
        
        if z_score > self.z_score_threshold:
            reduction_factor = max(0.1, 1.0 - (z_score / 10.0))
            return max(1, int(base_limit * reduction_factor))
            
        return base_limit