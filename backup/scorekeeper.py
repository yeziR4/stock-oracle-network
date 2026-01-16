# scorekeeper.py - Verifies predictions and updates reputation scores
from datetime import datetime, timedelta
from config import ALPHA_VANTAGE_KEY, STOCK_SYMBOL
import requests
import os

def read_predictions():
    """Read all predictions from file"""
    predictions = []
    
    if not os.path.exists("predictions.txt"):
        print("❌ No predictions file found!")
        return predictions
    
    try:
        with open("predictions.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(",")
                if len(parts) >= 5:
                    predictions.append({
                        "agent": parts[0],
                        "prediction": parts[1],
                        "confidence": parts[2],
                        "reasoning": parts[3],
                        "timestamp": parts[4]
                    })
        return predictions
    except Exception as e:
        print(f"❌ Error reading predictions: {e}")
        return predictions

def fetch_market_movement(days_ago=1):
    """Fetch whether market went UP or DOWN from X days ago to today"""
    try:
        # Get daily time series
        url = f"https://alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK_SYMBOL}&apikey={ALPHA_VANTAGE_KEY}"

        
        response = requests.get(url)
        data = response.json()
        
        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            dates = sorted(time_series.keys(), reverse=True)
            
            if len(dates) >= 2:
                # Compare today vs yesterday (or days_ago)
                today_close = float(time_series[dates[0]]["4. close"])
                yesterday_close = float(time_series[dates[days_ago]]["4. close"])
                
                movement = "UP" if today_close > yesterday_close else "DOWN"
                change = today_close - yesterday_close
                change_percent = (change / yesterday_close) * 100
                
                return {
                    "movement": movement,
                    "today_close": today_close,
                    "yesterday_close": yesterday_close,
                    "change": change,
                    "change_percent": change_percent,
                    "dates": {"today": dates[0], "yesterday": dates[days_ago]}
                }
        
        print(f"⚠️  API response: {data}")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching market movement: {e}")
        return None

def load_reputation_scores():
    """Load existing reputation scores"""
    scores = {}
    
    if os.path.exists("reputation_scores.txt"):
        try:
            with open("reputation_scores.txt", "r") as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split(",")
                    if len(parts) >= 3:
                        agent = parts[0]
                        correct = int(parts[1])
                        total = int(parts[2])
                        scores[agent] = {"correct": correct, "total": total}
        except Exception as e:
            print(f"⚠️  Error loading scores (starting fresh): {e}")
    
    return scores

def save_reputation_scores(scores):
    """Save reputation scores to file"""
    try:
        with open("reputation_scores.txt", "w") as f:
            for agent, stats in scores.items():
                correct = stats["correct"]
                total = stats["total"]
                percentage = (correct / total * 100) if total > 0 else 0
                f.write(f"{agent},{correct},{total},{percentage:.1f}%\n")
        print("💾 Reputation scores saved!")
    except Exception as e:
        print(f"❌ Error saving scores: {e}")

def verify_predictions(predictions, actual_movement):
    """Verify predictions against actual market movement"""
    print("\n🔍 Verifying Predictions...")
    print("=" * 60)
    
    scores = load_reputation_scores()
    
    for pred in predictions:
        agent = pred["agent"]
        predicted = pred["prediction"]
        actual = actual_movement["movement"]
        
        # Initialize agent if not in scores
        if agent not in scores:
            scores[agent] = {"correct": 0, "total": 0}
        
        # Check if prediction was correct
        is_correct = (predicted == actual)
        
        # Update scores
        scores[agent]["total"] += 1
        if is_correct:
            scores[agent]["correct"] += 1
        
        # Display result
        result_emoji = "✅" if is_correct else "❌"
        print(f"{result_emoji} {agent}:")
        print(f"   Predicted: {predicted} (Confidence: {pred['confidence']})")
        print(f"   Actual: {actual}")
        print(f"   Result: {'CORRECT' if is_correct else 'WRONG'}")
        print(f"   Score: {scores[agent]['correct']}/{scores[agent]['total']} ({scores[agent]['correct']/scores[agent]['total']*100:.1f}%)")
        print()
    
    return scores

def run_scorekeeper():
    """Run the scorekeeper agent"""
    print("🤖 Stock Oracle - Scorekeeper Agent")
    print("=" * 60)
    
    # Read predictions
    print("\n📖 Reading predictions...")
    predictions = read_predictions()
    
    if not predictions:
        print("❌ No predictions to verify!")
        return
    
    print(f"✅ Found {len(predictions)} prediction(s)")
    
    # Fetch actual market movement
    print("\n📊 Fetching actual market movement...")
    actual_movement = fetch_market_movement(days_ago=1)
    
    if not actual_movement:
        print("❌ Failed to fetch market data!")
        print("\n⚠️  NOTE: For testing, we'll simulate market movement")
        print("   In production, this would use real historical data")
        
        # SIMULATION for testing (remove this in production)
        actual_movement = {
            "movement": "DOWN",  # Simulated - change this to test
            "today_close": 693.77,
            "yesterday_close": 695.16,
            "change": -1.39,
            "change_percent": -0.20,
            "dates": {"today": "2026-01-14", "yesterday": "2026-01-13"}
        }
        print(f"\n🎭 SIMULATION MODE:")
    
    print(f"✅ Market Movement: {actual_movement['movement']}")
    print(f"   {actual_movement['dates']['yesterday']}: ${actual_movement['yesterday_close']}")
    print(f"   {actual_movement['dates']['today']}: ${actual_movement['today_close']}")
    print(f"   Change: {actual_movement['change']:.2f} ({actual_movement['change_percent']:.2f}%)")
    
    # Verify and update scores
    scores = verify_predictions(predictions, actual_movement)
    save_reputation_scores(scores)
    
    print("\n" + "=" * 60)
    print("📊 FINAL REPUTATION SCORES:")
    print("=" * 60)
    for agent, stats in scores.items():
        percentage = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{agent}: {stats['correct']}/{stats['total']} ({percentage:.1f}%)")
    
    print("\n✅ SCOREKEEPER COMPLETE!")

if __name__ == "__main__":
    run_scorekeeper() 
