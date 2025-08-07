"""
Gatenet Dashboard - Heroku Demo App
Simplified version of the dashboard for demonstration purposes.

Heroku demo app for Gatenet sandbox (https://gatenet.readthedocs.io/en/latest/sandbox.html)

- This is a simplified version optimized for demo purposes
"""
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import time
import random
import socket
import aiofiles

# Create FastAPI app
app = FastAPI(
    title="Gatenet Dashboard",
    description="Network diagnostics and monitoring dashboard",
    version="0.12.0"
)

# CORS middleware for iframe embedding
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
# Main dashboard page
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    async with aiofiles.open("static/index.html") as f:
        return await f.read()

@app.get("/api/ping")
async def api_ping(host: str = Query(..., description="Host to ping"), 
                 count: int = Query(3, ge=1, le=10)):
    """Ping a host and return statistics."""
    # Simulated ping for demo purposes
    await asyncio.sleep(0.5)  # Simulate network delay
    
    # Generate realistic ping data
    success = random.random() > 0.1  # 90% success rate
    
    if not success:
        return {"ok": False, "error": "Request timed out"}
        
    rtt_values = [round(random.uniform(15, 100), 2) for _ in range(count)]
    
    return {
        "ok": True, 
        "result": {
            "host": host,
            "success": True,
            "min_rtt": min(rtt_values),
            "max_rtt": max(rtt_values),
            "avg_rtt": sum(rtt_values) / len(rtt_values),
            "packet_loss": 0,
            "packets_sent": count,
            "packets_received": count,
            "rtts": rtt_values
        }
    }

@app.get("/api/dns_lookup")
async def api_dns_lookup(host: str = Query(..., description="Host to resolve")):
    """Perform DNS lookup on a host."""
    try:
        # This is safe to use in Heroku
        ip = socket.gethostbyname(host)
        return {"ok": True, "result": {"ip": ip, "host": host}}
    except socket.gaierror:
        return {"ok": False, "error": f"Could not resolve hostname: {host}"}

@app.get("/api/health")
async def health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.12.0",
        "timestamp": time.time()
    }