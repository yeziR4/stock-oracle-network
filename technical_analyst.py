# technical_analyst.py - P
# redicts stock movement using technical analysis

DEBUG = True

from groq import Groq
from datetime import datetime
from config import GROQ_API_KEY, STOCK_SYMBOL
import os

def read_market_data():
    """Read the latest market data"""
    try:
        with open("latest_market_data.txt", "r") as f:
            lines = f.readlines()
            timestamp = lines[0].strip()
            data_line = lines[1].strip()
            symbol, price, change_percent = data_line.split(",")
            return {
                "symbol": symbol,
                "price": float(price),
                "change_percent": change_percent,
                "timestamp": timestamp
            }
    except Exception as e:
        print(f"❌ Error reading market data: {e}")
        return None

def make_prediction(market_data):
    """Use Groq to make a technical prediction"""

    if DEBUG:
        print("\n🔍 DEBUG: Starting make_prediction()")

    if not GROQ_API_KEY or len(GROQ_API_KEY) < 10:
        print("❌ DEBUG ERROR: GROQ_API_KEY is missing or invalid")
        return None

    if DEBUG:
        print("✅ DEBUG: GROQ_API_KEY detected")
        print(f"✅ DEBUG: Using model llama-3.3-70b-versatile")
        print(f"✅ DEBUG: Market data sent → {market_data}")

    try:
        client = Groq(api_key=GROQ_API_KEY)

        prompt = f"""You are a technical analyst for stock market predictions.

Based on this current market data:
- Stock: {market_data['symbol']}
- Current Price: ${market_data['price']}
- Today's Change: {market_data['change_percent']}

Using technical analysis principles, predict: Will {market_data['symbol']} go UP or DOWN by market open tomorrow?

Respond in this EXACT format (no extra text):
PREDICTION: [UP or DOWN]
CONFIDENCE: [HIGH or MEDIUM or LOW]
REASONING: [One sentence explaining your technical analysis]"""

        if DEBUG:
            print("📤 DEBUG: Sending request to Groq...")

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a technical stock analyst. Be concise and follow the exact format requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )

        if DEBUG:
            print("📥 DEBUG: Received response from Groq")

        return completion.choices[0].message.content

    except Exception as e:
        print("❌ Groq API error occurred!")
        print(f"❌ ERROR TYPE: {type(e)}")
        print(f"❌ ERROR MESSAGE: {e}")

        if DEBUG:
            import traceback
            traceback.print_exc()

        return None


def parse_prediction(response):
    """Parse the prediction response"""
    lines = response.strip().split("\n")
    prediction_data = {}
    
    for line in lines:
        if "PREDICTION:" in line:
            prediction_data["prediction"] = line.split("PREDICTION:")[1].strip()
        elif "CONFIDENCE:" in line:
            prediction_data["confidence"] = line.split("CONFIDENCE:")[1].strip()
        elif "REASONING:" in line:
            prediction_data["reasoning"] = line.split("REASONING:")[1].strip()
    
    return prediction_data

def save_prediction(prediction_data):
    """Save prediction to file"""
    timestamp = datetime.now().isoformat()
    
    # Format: AGENT,PREDICTION,CONFIDENCE,REASONING,TIMESTAMP
    line = f"TechnicalAnalyst,{prediction_data['prediction']},{prediction_data['confidence']},{prediction_data['reasoning']},{timestamp}\n"
    
    # Append to predictions file
    with open("predictions.txt", "a") as f:
        f.write(line)
    
    print(f"💾 Prediction saved to predictions.txt")

def run_technical_analyst():
    """Run the technical analyst agent"""
    print("🤖 Stock Oracle - Technical Analyst Agent")
    print("=" * 60)
    if DEBUG:
        print("🔍 DEBUG MODE ENABLED")
        print(f"🔍 DEBUG: Python version OK")
    # Read market data
    print("\n📖 Reading market data...")
    market_data = read_market_data()
    
    if not market_data:
        print("❌ Failed to read market data. Run data_collector.py first!")
        return
    
    print(f"✅ Loaded: {market_data['symbol']} at ${market_data['price']} ({market_data['change_percent']})")
    
    # Make prediction
    print("\n🧠 Analyzing with AI...")
    response = make_prediction(market_data)
    
    if not response:
        print("❌ Failed to get prediction from Groq")
        return
    
    print(f"\n📊 Raw AI Response:\n{response}\n")
    
    # Parse and save
    prediction_data = parse_prediction(response)
    
    if prediction_data:
        print("✅ Prediction parsed successfully:")
        print(f"   Prediction: {prediction_data.get('prediction', 'N/A')}")
        print(f"   Confidence: {prediction_data.get('confidence', 'N/A')}")
        print(f"   Reasoning: {prediction_data.get('reasoning', 'N/A')}")
        
        save_prediction(prediction_data)
        print("\n✅ TECHNICAL ANALYST COMPLETE!")
    else:
        print("❌ Failed to parse prediction")

if __name__ == "__main__":
    run_technical_analyst() 
