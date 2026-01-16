# sentiment_analyst.py — AI-driven news sentiment analyst
from groq import Groq
from datetime import datetime
from config import GROQ_API_KEY, NEWS_API_KEY
import requests
import json

MODEL = "llama-3.3-70b-versatile"


# -------------------------------------------------------------------
# Fetch RAW headlines (intentionally broad)
# -------------------------------------------------------------------
def fetch_news_headlines():
    try:
        url = (
            "https://newsapi.org/v2/everything?"
            "q=market OR stocks OR economy OR Wall Street OR SPY OR S&P 500&"
            "language=en&sortBy=publishedAt&pageSize=15&"
            f"apiKey={NEWS_API_KEY}"
        )

        r = requests.get(url, timeout=10)
        data = r.json()

        if data.get("status") == "ok":
            return [
                article.get("title", "")
                for article in data.get("articles", [])
                if article.get("title")
            ]

    except Exception as e:
        print(f"⚠️ NewsAPI error: {e}")

    # Safe fallback
    return [
        "US stock futures trade cautiously ahead of economic data",
        "Wall Street investors assess Federal Reserve policy outlook",
        "Markets show mixed momentum amid inflation uncertainty",
        "Equities remain range-bound as traders await earnings guidance"
    ]


# -------------------------------------------------------------------
# Read market data
# -------------------------------------------------------------------
def read_market_data():
    try:
        with open("latest_market_data.txt", "r") as f:
            lines = f.readlines()
            symbol, price, change = lines[1].strip().split(",")
            return {
                "symbol": symbol,
                "price": float(price),
                "change_percent": change
            }
    except Exception as e:
        print(f"❌ Market data error: {e}")
        return None


# -------------------------------------------------------------------
# AI Tool: Select relevant headlines
# -------------------------------------------------------------------
def select_relevant_headlines(client, headlines):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "select_relevant_headlines",
                "description": "Select only US stock-market relevant headlines",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "headlines": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["headlines"]
                }
            }
        }
    ]

    system_prompt = (
        "You are a professional financial news editor.\n"
        "From the provided headlines, select ONLY those relevant to:\n"
        "- US stock market\n"
        "- SPY / S&P 500\n"
        "- Federal Reserve, inflation, interest rates\n"
        "- Market sentiment or earnings\n\n"
        "If none are relevant, return an empty list."
    )

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "\n".join(headlines)}
        ],
        tools=tools,
        tool_choice="auto",
        temperature=0
    )

    tool_call = completion.choices[0].message.tool_calls
    if not tool_call:
        return []

    args = json.loads(tool_call[0].function.arguments)
    return args.get("headlines", [])


# -------------------------------------------------------------------
# AI Sentiment Prediction
# -------------------------------------------------------------------
def make_prediction(market_data, headlines):
    client = Groq(api_key=GROQ_API_KEY)

    relevant_headlines = select_relevant_headlines(client, headlines)

    if not relevant_headlines:
        relevant_headlines = [
            "No materially market-moving news detected in the latest cycle"
        ]

    headlines_text = "\n".join(f"- {h}" for h in relevant_headlines)

    prompt = f"""
You are a professional market sentiment analyst.

Market data:
- Asset: {market_data['symbol']}
- Price: ${market_data['price']}
- Daily Change: {market_data['change_percent']}

Relevant news headlines:
{headlines_text}

Based strictly on sentiment impact, predict tomorrow's market direction.

Respond in EXACT format:
PREDICTION: [UP or DOWN]
CONFIDENCE: [HIGH or MEDIUM or LOW]
REASONING: [One clear sentence]
"""

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Follow format strictly. Be objective."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=120
    )

    print("\n📰 AI-SELECTED RELEVANT HEADLINES:")
    for h in relevant_headlines:
        print(f"  • {h}")

    return completion.choices[0].message.content


# -------------------------------------------------------------------
# Parse response
# -------------------------------------------------------------------
def parse_prediction(text):
    result = {}
    for line in text.splitlines():
        if line.startswith("PREDICTION:"):
            result["prediction"] = line.split(":", 1)[1].strip()
        elif line.startswith("CONFIDENCE:"):
            result["confidence"] = line.split(":", 1)[1].strip()
        elif line.startswith("REASONING:"):
            result["reasoning"] = line.split(":", 1)[1].strip()
    return result


# -------------------------------------------------------------------
# Save output
# -------------------------------------------------------------------
def save_prediction(data):
    timestamp = datetime.now().isoformat()
    line = (
        f"SentimentAnalyst,{data['prediction']},"
        f"{data['confidence']},{data['reasoning']},{timestamp}\n"
    )
    with open("predictions.txt", "a") as f:
        f.write(line)


# -------------------------------------------------------------------
# Main runner
# -------------------------------------------------------------------
def run_sentiment_analyst():
    print("🤖 Stock Oracle — Sentiment Analyst")
    print("=" * 60)

    market_data = read_market_data()
    if not market_data:
        return

    headlines = fetch_news_headlines()

    response = make_prediction(market_data, headlines)
    print("\n📊 AI RESPONSE:\n", response)

    parsed = parse_prediction(response)
    save_prediction(parsed)

    print("\n✅ SENTIMENT ANALYSIS COMPLETE")


if __name__ == "__main__":
    run_sentiment_analyst()
