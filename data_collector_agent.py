# data_collector_agent.py - OpenAgents WorkerAgent version
from openagents.agents.worker_agent import WorkerAgent
from openagents.models.event_context import EventContext
import requests
from datetime import datetime
from config import ALPHA_VANTAGE_KEY, STOCK_SYMBOL
import asyncio

class DataCollectorAgent(WorkerAgent):
    """Agent that fetches and broadcasts stock market data."""
    
    default_agent_id = "market_data_collector"
    
    async def on_startup(self):
        """Called when agent starts - fetch and broadcast market data"""
        print("🚀 Market Data Collector Agent started!")
        
        # Debug: show available mods
        print(f"Available mod adapters: {list(self.client.mod_adapters.keys())}")
        
        print("Fetching initial market data...")
    
    async def on_shutdown(self):
        """Called when agent shuts down."""
        print("Market Data Collector stopped.")
    
    async def broadcast_market_data(self):
        """Fetch and broadcast market data to the network"""
        try:
            # Fetch market data
            market_data = self.fetch_stock_price()
            
            if market_data:
                # Format message
                message = f"""📊 **Market Data Update**
Symbol: {market_data['symbol']}
Price: ${market_data['price']}
Change: {market_data['change']} ({market_data['change_percent']})
Timestamp: {market_data['timestamp']}"""
                
                # Send to market-data channel
                # Try different ways to get messaging adapter
                messaging = (
                    self.client.mod_adapters.get("openagents.mods.workspace.messaging") or
                    self.client.mod_adapters.get("messaging") or
                    self.client.mod_adapters.get("workspace.messaging")
                )
                if messaging:
                    await messaging.send_channel_message(
                        channel="market-data",
                        text=message
                    )
                    print(f"✅ Posted market data to #market-data channel")
                    print(f"   {market_data['symbol']}: ${market_data['price']} ({market_data['change_percent']})")
                else:
                    print("❌ Messaging adapter not available")
                
                # Also save to file for backup
                with open("latest_market_data.txt", "w") as f:
                    f.write(f"{market_data['timestamp']}\n")
                    f.write(f"{market_data['symbol']},{market_data['price']},{market_data['change_percent']}\n")
                
                return market_data
            else:
                print("❌ Failed to fetch market data")
                return None
                
        except Exception as e:
            print(f"❌ Error broadcasting market data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def fetch_stock_price(self):
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
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "symbol": STOCK_SYMBOL,
                    "price": float(price) if price != "N/A" else None,
                    "change": change,
                    "change_percent": change_percent
                }
            else:
                print(f"API Error: {data}")
                return None
                
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

async def main():
    """Run the market data collector agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Market Data Collector Agent")
    parser.add_argument("--host", default="localhost", help="Network host")
    parser.add_argument("--port", type=int, default=8700, help="Network port")
    args = parser.parse_args()
    
    agent = DataCollectorAgent()
    
    try:
        print(f"Connecting to network at {args.host}:{args.port}...")
        await agent.async_start(
            network_host=args.host,
            network_port=args.port,
        )
        
        # Keep running
        print("\nAgent is running... Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(60)  # Sleep for 60 seconds
            # Optionally: fetch new data every minute
            # await agent.broadcast_market_data()
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.async_stop()

if __name__ == "__main__":
    asyncio.run(main())