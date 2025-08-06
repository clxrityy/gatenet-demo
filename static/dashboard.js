document.addEventListener('DOMContentLoaded', () => {
    // Ping functionality
    const pingButton = document.getElementById('ping-button');
    const pingHost = document.getElementById('ping-host');
    const pingCount = document.getElementById('ping-count');
    const pingResults = document.getElementById('ping-results');
    
    pingButton.addEventListener('click', async () => {
        const host = pingHost.value.trim();
        const count = pingCount.value;
        
        if (!host) {
            showError(pingResults, 'Please enter a valid host');
            return;
        }
        
        showLoading(pingResults);
        
        try {
            const response = await fetch(`/api/ping?host=${encodeURIComponent(host)}&count=${count}`);
            const data = await response.json();
            
            if (data.ok) {
                const result = data.result;
                let output = `PING ${result.host} (${result.host}): statistics\n`;
                output += `${result.packets_sent} packets transmitted, ${result.packets_received} received, ${result.packet_loss}% packet loss\n`;
                output += `round-trip min/avg/max = ${result.min_rtt.toFixed(2)}/${result.avg_rtt.toFixed(2)}/${result.max_rtt.toFixed(2)} ms\n`;
                
                if (result.rtts && result.rtts.length > 0) {
                    output += '\nIndividual RTTs:\n';
                    result.rtts.forEach((rtt, i) => {
                        output += `Packet ${i+1}: ${rtt} ms\n`;
                    });
                }
                
                showOutput(pingResults, output);
            } else {
                showError(pingResults, data.error || 'Ping failed');
            }
        } catch (error) {
            showError(pingResults, 'Request failed: ' + error.message);
        }
    });
    
    // Traceroute functionality
    const tracerouteButton = document.getElementById('traceroute-button');
    const tracerouteHost = document.getElementById('traceroute-host');
    const tracerouteResults = document.getElementById('traceroute-results');
    
    tracerouteButton.addEventListener('click', async () => {
        const host = tracerouteHost.value.trim();
        
        if (!host) {
            showError(tracerouteResults, 'Please enter a valid host');
            return;
        }
        
        showLoading(tracerouteResults);
        
        try {
            const response = await fetch(`/api/traceroute?host=${encodeURIComponent(host)}`);
            const data = await response.json();
            
            if (data.ok && data.hops) {
                let output = `traceroute to ${host}\n\n`;
                
                data.hops.forEach(hop => {
                    const hostname = hop.hostname ? `(${hop.hostname})` : '';
                    output += `${hop.hop.toString().padStart(2)}  ${hop.ip} ${hostname.padEnd(20)} ${hop.rtt} ms\n`;
                });
                
                showOutput(tracerouteResults, output);
            } else {
                showError(tracerouteResults, data.error || 'Traceroute failed');
            }
        } catch (error) {
            showError(tracerouteResults, 'Request failed: ' + error.message);
        }
    });
    
    // DNS lookup functionality
    const dnsButton = document.getElementById('dns-button');
    const dnsHost = document.getElementById('dns-host');
    const dnsResults = document.getElementById('dns-results');
    
    dnsButton.addEventListener('click', async () => {
        const host = dnsHost.value.trim();
        
        if (!host) {
            showError(dnsResults, 'Please enter a valid host');
            return;
        }
        
        showLoading(dnsResults);
        
        try {
            const response = await fetch(`/api/dns_lookup?host=${encodeURIComponent(host)}`);
            const data = await response.json();
            
            if (data.ok && data.result) {
                let output = `DNS lookup for ${host}\n\n`;
                output += `Result: ${data.result.host} -> ${data.result.ip}\n`;
                showOutput(dnsResults, output);
            } else {
                showError(dnsResults, data.error || 'DNS lookup failed');
            }
        } catch (error) {
            showError(dnsResults, 'Request failed: ' + error.message);
        }
    });
    
    // Port scan functionality
    const portButton = document.getElementById('port-button');
    const portHost = document.getElementById('port-host');
    const portPorts = document.getElementById('port-ports');
    const portResults = document.getElementById('port-results');
    
    portButton.addEventListener('click', async () => {
        const host = portHost.value.trim();
        const ports = portPorts.value.trim();
        
        if (!host) {
            showError(portResults, 'Please enter a valid host');
            return;
        }
        
        if (!ports) {
            showError(portResults, 'Please enter ports to scan');
            return;
        }
        
        showLoading(portResults);
        
        try {
            const response = await fetch(`/api/port_scan?host=${encodeURIComponent(host)}&ports=${encodeURIComponent(ports)}`);
            const data = await response.json();
            
            if (data.ok && data.result) {
                let output = `Port scan results for ${host}\n\n`;
                
                if (data.result.ports && data.result.ports.length > 0) {
                    output += 'PORT\tSTATUS\tSERVICE\n';
                    output += '-----------------------------\n';
                    
                    data.result.ports.forEach(port => {
                        const status = port.status === 'open' ? 'OPEN' : 'closed';
                        const statusFormatted = status === 'OPEN' ? '\x1b[32mOPEN\x1b[0m' : '\x1b[31mclosed\x1b[0m';
                        output += `${port.port}\t${statusFormatted}\t${port.service || '-'}\n`;
                    });
                } else {
                    output += 'No ports were scanned.';
                }
                
                showOutput(portResults, output);
            } else {
                showError(portResults, data.error || 'Port scan failed');
            }
        } catch (error) {
            showError(portResults, 'Request failed: ' + error.message);
        }
    });
    
    // Helper functions
    function showLoading(container) {
        const loading = container.querySelector('.loading');
        const output = container.querySelector('.output');
        
        if (loading) loading.style.display = 'flex';
        if (output) output.style.display = 'none';
    }
    
    function showOutput(container, text) {
        const loading = container.querySelector('.loading');
        const output = container.querySelector('.output');
        
        if (loading) loading.style.display = 'none';
        if (output) {
            output.style.display = 'block';
            output.textContent = text;
        }
    }
    
    function showError(container, text) {
        const loading = container.querySelector('.loading');
        const output = container.querySelector('.output');
        
        if (loading) loading.style.display = 'none';
        if (output) {
            output.style.display = 'block';
            output.textContent = 'Error: ' + text;
            output.style.color = 'var(--danger)';
            
            // Reset color after 3 seconds
            setTimeout(() => {
                output.style.color = 'var(--text-light)';
            }, 3000);
        }
    }
});