"""
Gatenet Dashboard - Heroku Demo App
Simplified version of the dashboard for demonstration purposes.

Heroku demo app for Gatenet sandbox (https://gatenet.readthedocs.io/en/latest/sandbox.html)

- This is a simplified version optimized for demo purposes
"""
import os
import asyncio
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import aiofiles

# Create FastAPI app
app = FastAPI(
    title="Gatenet Dashboard",
    description="Network diagnostics and monitoring dashboard",
    version="0.12.0"
)

# Add CORS for iframe embedding in the docs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

ERROR_MESSAGE = "An error occurred processing your request"

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the main dashboard HTML."""
    async with aiofiles.open("static/index.html") as f:
        return await f.read()

# API endpoints
@app.get("/api/ping")
async def api_ping(host: str = Query(..., description="Host to ping"), 
                  count: int = Query(3, ge=1, le=10)):
    """Ping a host and return the result."""
    try:
        # Simulate ping for demo (real implementation would use gatenet.diagnostics.ping)
        import random
        # Simulate network delay
        await asyncio.sleep(0.5)

        # Generate realistic ping response
        success = random.random() > 0.1  # 10% failure rate
        
        if not success:
            return {"ok": False, "error": "Request timed out"}
            
        rtt_values = [random.uniform(15, 100) for _ in range(count)]
        
        return {
            "ok": True, 
            "result": {
                "host": host,
                "success": True,
                "raw_output": f"PING {host} 56 data bytes\n" + "\n".join([
                    f"64 bytes from {host}: icmp_seq={i+1} ttl=57 time={rtt:.2f} ms" 
                    for i, rtt in enumerate(rtt_values)
                ]),
                "min_rtt": min(rtt_values),
                "max_rtt": max(rtt_values),
                "avg_rtt": sum(rtt_values) / len(rtt_values),
                "packet_loss": 0,
                "packets_sent": count,
                "packets_received": count,
                "jitter": round(max(rtt_values) - min(rtt_values), 2),
                "rtts": [round(rtt, 2) for rtt in rtt_values]
            }
        }
    except Exception:
        return {"ok": False, "error": ERROR_MESSAGE}

def _generate_hop_ip(host: str, hop_index: int, hop_count: int, base_ip: str) -> str:
    """Generate IP address for a hop."""
    import random
    import socket
    
    if hop_index == hop_count - 1:
        # Last hop is the destination
        return socket.gethostbyname(host) if random.random() > 0.3 else f"203.0.113.{random.randint(1, 254)}"
    elif hop_index < 3:
        return f"{base_ip}{hop_index+1}"
    else:
        return f"203.0.113.{random.randint(1, 254)}"

def _generate_hop_hostname(host: str, hop_index: int, hop_count: int) -> str:
    """Generate hostname for a hop."""
    import random
    
    if hop_index == hop_count - 1:
        return host if random.random() > 0.3 else ""
    else:
        return f"router-{hop_index+1}.example.com" if random.random() > 0.7 else ""

def _generate_traceroute_hops(host: str) -> list:
    """Generate simulated traceroute hops."""
    import random
    
    hops = []
    base_ip = "10.0.0."
    hop_count = random.randint(5, 12)
    current_rtt = 5.0
    
    for i in range(hop_count):
        ip = _generate_hop_ip(host, i, hop_count, base_ip)
        hostname = _generate_hop_hostname(host, i, hop_count)
        current_rtt += random.uniform(5, 15)
        
        hops.append({
            "hop": i+1,
            "ip": ip,
            "hostname": hostname,
            "rtt": round(current_rtt, 2)
        })
    
    return hops

@app.get("/api/traceroute")
async def api_traceroute(host: str = Query(..., description="Host to traceroute")):
    """Traceroute to a host and return hops."""
    try:
        # Simulate network delay
        await asyncio.sleep(1)
        
        hops = _generate_traceroute_hops(host)
        return {"ok": True, "hops": hops}
    except Exception:
        return {"ok": False, "error": ERROR_MESSAGE}

@app.get("/api/dns_lookup")
async def api_dns_lookup(host: str = Query(..., description="Host to resolve")):
    """Perform DNS lookup on a host."""
    try:
        # Actual DNS lookup (safe to use in Heroku)
        import socket
        try:
            ip = socket.gethostbyname(host)
            return {"ok": True, "result": {"ip": ip, "host": host}}
        except socket.gaierror:
            return {"ok": False, "error": f"Could not resolve hostname: {host}"}
    except Exception:
        return {"ok": False, "error": "An error occurred processing your request"}

@app.get("/api/port_scan")
async def api_port_scan(
    host: str = Query(..., description="Host to scan"), 
    ports: str = Query("80,443,22,21,25", description="Comma-separated ports")
):
    """Scan ports on a host (simulated for demo)."""
    try:
        # Simulate port scan for demo
        import random
        import time
        # Simulate network delay
        await asyncio.sleep(1.5)
        
        # Parse ports
        port_list = [int(p.strip()) for p in ports.split(",") if p.strip().isdigit()]
        if not port_list:
            return {"ok": False, "error": "No valid ports provided"}
            
        if len(port_list) > 20:
            return {"ok": False, "error": "Maximum 20 ports allowed for scan"}
        
        # Generate realistic port scan results
        common_open_ports = [80, 443, 22]  # These are commonly open
        results = []
        
        for port in port_list:
            # Common ports more likely to be open
            is_open = port in common_open_ports and random.random() > 0.2
            
            # Other ports rarely open
            if port not in common_open_ports:
                is_open = random.random() > 0.9
                
            service = ""
            if is_open:
                services = {
                    22: "SSH",
                    21: "FTP", 
                    25: "SMTP",
                    80: "HTTP",
                    443: "HTTPS",
                    3306: "MySQL",
                    5432: "PostgreSQL"
                }
                service = services.get(port, "")
                
            results.append({
                "port": port,
                "status": "open" if is_open else "closed",
                "service": service
            })
            
        return {"ok": True, "result": {"host": host, "ports": results}}
    except Exception:
        return {"ok": False, "error": ERROR_MESSAGE}

@app.get("/api/health")
async def health_check():
    """API health check endpoint."""
    return {"status": "healthy", "version": "0.12.0"}

# Run the app
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)