class MetricsCollector:
    def __init__(self, redis_client):
        self.redis = redis_client

    def record_request(self, client_id: str, allowed: bool):
        status = "allowed" if allowed else "blocked"
        self.redis.hincrby("ratekeep:metrics:requests", status, 1)
        self.redis.hincrby(f"ratekeep:metrics:client:{client_id}", status, 1)

    def record_anomaly_score(self, client_id: str, score: float):
        self.redis.hset("ratekeep:metrics:anomaly", client_id, score)

    def export_prometheus(self) -> str:
        lines = []
        requests = self.redis.hgetall("ratekeep:metrics:requests")
        allowed = int(requests.get(b"allowed", 0))
        blocked = int(requests.get(b"blocked", 0))
        
        lines.append(f'ratekeep_requests_total{{status="allowed"}} {allowed}')
        lines.append(f'ratekeep_requests_total{{status="blocked"}} {blocked}')
        
        anomaly_scores = self.redis.hgetall("ratekeep:metrics:anomaly")
        for client_id, score in anomaly_scores.items():
            cid = client_id.decode("utf-8")
            val = float(score)
            lines.append(f'ratekeep_anomaly_score{{client_id="{cid}"}} {val}')
                
        return "\n".join(lines) + "\n"