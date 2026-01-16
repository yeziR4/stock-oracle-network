# Stock Oracle Network

Multi-agent prediction system for stock market forecasting with reputation tracking.

## Status: Work in Progress

Built for the OpenAgents PR Hackathon (January 2026). Currently implementing OpenAgents WorkerAgent integration.

## What Works

- ✅ Market data collector (Alpha Vantage API)
- ✅ Technical analyst agent (Groq AI)
- ✅ Sentiment analyst agent (NewsAPI + Groq AI)
- ✅ Scorekeeper with reputation tracking
- ✅ File-based agent communication (backup/testing)

## Architecture

### Current Implementation (Functional)
**File-based communication:**
- Agents communicate via shared text files
- `data_collector.py` → fetches SPY market data
- `technical_analyst.py` → analyzes price patterns
- `sentiment_analyst.py` → analyzes news sentiment
- `scorekeeper.py` → verifies predictions and tracks reputation
- Modular, testable, fully functional

### Target Implementation (In Progress)
**OpenAgents WorkerAgent integration:**
- Converting agents to WorkerAgent framework
- Network server running on localhost:8700 (HTTP) / 8600 (gRPC)
- Agents connect successfully via gRPC
- Working on channel-based communication

## Current Challenge

Agents connect to OpenAgents network successfully, but messaging mod adapter is not available.

**Symptoms:**
- Network created via `openagents network init`
- `network.yaml` shows `openagents.mods.workspace.messaging` enabled
- Agent connects: `GRPCNetworkConnector(connected=True)`
- System events work: `✅ EVENT SENT: system.list_mods`
- But `self.client.mod_adapters` only returns: `['openagents.mods.games.agentworld']`

**Question for contributors:**
Why would messaging mod not load for WorkerAgents despite being enabled in network config?

## Setup

### Prerequisites
```bash
pip install openagents groq requests
```

### API Keys
Create `config.py`:
```python
ALPHA_VANTAGE_KEY = "your_key"
NEWS_API_KEY = "your_key"
GROQ_API_KEY = "your_key"
STOCK_SYMBOL = "SPY"
```

### Run File-Based Version
```bash
# Terminal 1: Collect market data
python data_collector.py

# Terminal 2: Technical analysis
python technical_analyst.py

# Terminal 3: Sentiment analysis
python sentiment_analyst.py

# Terminal 4: Verify and score
python scorekeeper.py
```

### Run OpenAgents Version (WIP)
```bash
# Terminal 1: Start network
openagents network start ./stock-oracle-network-openagents

# Terminal 2: Run agent
python data_collector_agent.py
```

## Project Structure
```
stock-oracle-network/
├── config.py                       # API keys (gitignored)
├── data_collector.py              # Fetches market data
├── technical_analyst.py           # Price pattern analysis
├── sentiment_analyst.py           # News sentiment analysis
├── scorekeeper.py                 # Prediction verification
├── data_collector_agent.py        # OpenAgents version (WIP)
├── network_config.py              # Network metadata
├── latest_market_data.txt         # Shared data file
├── predictions.txt                # Agent predictions
├── reputation_scores.txt          # Accuracy tracking
└── stock-oracle-network-openagents/
    └── network.yaml               # OpenAgents network config
```

## How It Works

1. **Data Collector** fetches real-time SPY stock price
2. **Technical Analyst** predicts UP/DOWN based on price patterns
3. **Sentiment Analyst** predicts UP/DOWN based on news headlines
4. **Scorekeeper** verifies predictions against actual market movement
5. **Reputation scores** track which agents are most accurate over time

## Next Steps

- [ ] Debug messaging mod adapter loading
- [ ] Convert remaining agents to WorkerAgent pattern
- [ ] Implement channel-based communication (#market-data, #predictions, #scores)
- [ ] Add demo video
- [ ] Complete documentation

## Contributing

This is a hackathon project but feedback welcome! Especially on the OpenAgents integration challenge.

## License

MIT 
