# network_config.py - Simplified for now, we'll use WorkerAgent properly later
# For Day 1, we're just proving the data collector works

def get_network_info():
    """Return basic network information"""
    return {
        "name": "stock-oracle-network",
        "description": "AI agents predicting stock movements with reputation tracking"
    }