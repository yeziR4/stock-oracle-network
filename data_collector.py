# data_collector.py - Fetches stock data (Day 1: Proving it works)
import requests
from datetime import datetime
from config import ALPHA_VANTAGE_KEY, STOCK_SYMBOL
from network_config import get_network_info

def fetch_stock_price():
    """Fetch current S&P 500 price from Alpha Vantage"""
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={STOCK_SYMBOL}&apikey={ALPHA_VANTAGE_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "Global Quote" in data:
            quote = data["Global Quote"]
            price = quote.get("05. price", "N/A")
            change = quote.get("09. change", "N/A")
            change_percent = quote.get("10. change percent", "N/A")
            
            market_data = {
                "timestamp": datetime.now().isoformat(),
                "symbol": STOCK_SYMBOL,
                "price": float(price) if price != "N/A" else None,
                "change": change,
                "change_percent": change_percent,
                "raw_message": f"📊 {STOCK_SYMBOL} at ${price} ({change_percent})"
            }
            
            return market_data
        else:
            print(f"API Error: {data}")
            return None
            
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def run_data_collector():
    """Run the data collector"""
    print("🚀 Stock Oracle - Market Data Collector")
    print("=" * 50)
    
    network_info = get_network_info()
    print(f"Network: {network_info['name']}")
    print(f"Agent: MarketDataCollector")
    print("\n📡 Fetching market data...\n")
    
    # Fetch data
    market_data = fetch_stock_price()
    
    if market_data:
        print(f"✅ Data fetched successfully!")
        print(f"   Symbol: {market_data['symbol']}")
        print(f"   Price: ${market_data['price']}")
        print(f"   Change: {market_data['change']} ({market_data['change_percent']})")
        print(f"\n📤 Message: {market_data['raw_message']}")
        
        # Save to file so other agents can read it
        with open("latest_market_data.txt", "w") as f:
            f.write(f"{market_data['timestamp']}\n")
            f.write(f"{market_data['symbol']},{market_data['price']},{market_data['change_percent']}\n")
        
        print("\n💾 Saved to latest_market_data.txt")
        print("\n✅ DAY 1 COMPLETE: Data collector working!")
        return market_data
    else:
        print("❌ Failed to fetch data")
        return None

if __name__ == "__main__":
    run_data_collector()