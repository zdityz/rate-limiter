# 🚦 Rate Limiter Microservice

A highly performant, asynchronous application-layer rate limiter built with **FastAPI** and **Redis**. 

This project implements the three industry-standard rate limiting algorithms to protect API endpoints from abuse, manage traffic bursts, and enforce fair usage quotas. It includes a real-time React dashboard for telemetry and visualization.

## ✨ Features
* **Abstract Base Class Architecture:** Easily extensible design to add new rate-limiting algorithms.
* **Asynchronous Redis Operations:** Utilizes `redis.asyncio` to prevent event-loop blocking under heavy load.
* **Atomic Pipeline Execution:** Uses Redis pipelines for commands like `ZREMRANGEBYSCORE` and `ZCARD` to ensure thread-safe, high-concurrency accuracy.
* **Live Telemetry:** Tracks global throughput, block rates, and per-user metrics in real-time.
* **Interactive Dashboard:** A React/Vite frontend to visually demonstrate the behavior of different limiting strategies.

## 🧠 Supported Algorithms

1. **Fixed Window (`/fixed`)**
   * Divides time into rigid segments. Simple and memory-efficient, but susceptible to traffic spikes at the edges of the window boundaries.
2. **Sliding Window (`/sliding`)**
   * Uses Redis Sorted Sets to track exact request timestamps. Highly accurate and eliminates the edge-spike problem, trading off slightly higher memory usage.
3. **Token Bucket (`/token`)**
   * The industry standard. Allows for sudden bursts of traffic while maintaining a steady, long-term processing rate. 

## 🛠️ Tech Stack
* **Backend:** Python 3, FastAPI, Uvicorn, Pydantic
* **In-Memory Datastore:** Redis
* **Frontend:** React, Vite, Axios
* **Testing:** Pytest, FastAPI TestClient

## 🔌 How to Integrate in Your Projects

This project is designed to run as an independent microservice within your Virtual Private Cloud (VPC). You can easily integrate it into your main application using a middleware or API Gateway approach. 

By routing requests through this service before hitting your heavy database or compute logic, you offload the rate-limiting overhead.

```python
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()
RATE_LIMITER_URL = "http://localhost:8000/token"

@app.get("/api/v1/protected-data/{item_id}")
async def get_data(item_id: str, user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{RATE_LIMITER_URL}/{user_id}")
        
    if response.status_code == 429:
        raise HTTPException(status_code=429, detail="Too many requests")
        
    return {"status": "success", "data": f"Accessing item {item_id}"}
```
## 🚀 Quick Start
* 1. Prerequisites
    - Python 3.9+
    - Node.js & npm
    - A running Redis instance
* 2. Run the Backend

    ```bash
    git clone [https://github.com/YOUR_USERNAME/rate-limiter.git](https://github.com/YOUR_USERNAME/rate-limiter.git)
    cd rate-limiter
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install pydantic-settings redis uvicorn[standard]
    uvicorn main:app --reload
    ```
* 3. Run the Dashboard

    ```bash
    cd frontend
    npm install
    npm run dev
    ```

## 📊 API Endpoints
* `POST /{algorithm}/{user_id}`: Attempts to process a request for a specific user using the chosen algorithm (fixed, sliding, or token).
* `GET /stats`: Returns global system telemetry (total requests, allowed, blocked, active users, throughput).
* `GET /stats/{user_id}`: Returns rate-limit metrics for a specific user.

## 🤝 Contributing

While this is primarily a portfolio project, contributions, issues, and feature requests are highly encouraged! If you have suggestions for improving the algorithms or adding new features (like distributed locking), feel free to fork the repo and create a pull request.

## 📜 License

Distributed under the MIT License. This means you are free to use, modify, and integrate this microservice into your own commercial or personal projects.

---
*If you found this project helpful or interesting, please consider giving it a ⭐ on GitHub!*