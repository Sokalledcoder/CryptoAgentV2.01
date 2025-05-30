from google.adk.agents import LlmAgent

# Define MCP tool functions for this agent
async def mcp_fearandgreed_get_current(random_string: str = "dummy") -> dict:
    """
    Gets the current Fear and Greed Index value.
    """
    print(f"[SentimentAgent Tool] mcp_fearandgreed_get_current called")
    # Simulate MCP call - in real implementation this would call the actual MCP server
    return {
        "value": 42,
        "value_classification": "Fear",
        "timestamp": 1735603200,
        "time_until_update": "12 hours"
    }

async def mcp_fearandgreed_interpret_value(value: int) -> dict:
    """
    Interprets a Fear and Greed Index value.
    """
    print(f"[SentimentAgent Tool] mcp_fearandgreed_interpret_value called with value: {value}")
    # Simulate interpretation based on value ranges
    if value <= 25:
        classification = "Extreme Fear"
        interpretation = "Market is in extreme fear, potentially oversold conditions"
    elif value <= 45:
        classification = "Fear"
        interpretation = "Market sentiment is fearful, caution advised"
    elif value <= 55:
        classification = "Neutral"
        interpretation = "Market sentiment is neutral, balanced conditions"
    elif value <= 75:
        classification = "Greed"
        interpretation = "Market sentiment is greedy, potential for correction"
    else:
        classification = "Extreme Greed"
        interpretation = "Market is in extreme greed, potentially overbought"
    
    return {
        "value": value,
        "classification": classification,
        "interpretation": interpretation
    }

async def mcp_fearandgreed_compare_with_historical(days: int = 30) -> dict:
    """
    Compares current Fear and Greed Index with historical data.
    """
    print(f"[SentimentAgent Tool] mcp_fearandgreed_compare_with_historical called with days: {days}")
    # Simulate historical comparison
    return {
        "current_value": 42,
        "average_last_30_days": 38,
        "comparison": "Current value is 4 points higher than 30-day average",
        "trend": "slightly_improving",
        "notes": "Fear levels have decreased slightly over the past month"
    }

async def global_market_data(include_defi: bool = False) -> dict:
    """
    Gets global cryptocurrency market data including BTC dominance and total market cap.
    """
    print(f"[SentimentAgent Tool] global_market_data called with include_defi: {include_defi}")
    # Simulate global market data
    return {
        "data": {
            "active_cryptocurrencies": 15234,
            "upcoming_icos": 0,
            "ongoing_icos": 49,
            "ended_icos": 3376,
            "markets": 1058,
            "total_market_cap": {
                "btc": 35234567.89,
                "eth": 1234567890.12,
                "ltc": 45678901234.56,
                "bch": 12345678901.23,
                "bnb": 9876543210.98,
                "eos": 8765432109.87,
                "xrp": 7654321098.76,
                "xlm": 6543210987.65,
                "link": 5432109876.54,
                "dot": 4321098765.43,
                "yfi": 3210987654.32,
                "usd": 3456789012345.67,
                "aed": 12691234567890.12,
                "ars": 3456789012345678.90
            },
            "total_volume": {
                "btc": 1234567.89,
                "eth": 12345678.90,
                "ltc": 123456789.01,
                "bch": 1234567890.12,
                "bnb": 12345678901.23,
                "eos": 123456789012.34,
                "xrp": 1234567890123.45,
                "xlm": 12345678901234.56,
                "link": 123456789012345.67,
                "dot": 1234567890123456.78,
                "yfi": 12345678901234567.89,
                "usd": 123456789012.34,
                "aed": 453456789012345.67,
                "ars": 12345678901234567890.12
            },
            "market_cap_percentage": {
                "btc": 56.78,
                "eth": 12.34,
                "usdt": 5.67,
                "bnb": 3.45,
                "sol": 2.89,
                "usdc": 2.34,
                "xrp": 1.78,
                "steth": 1.23,
                "doge": 0.98,
                "ada": 0.87
            },
            "market_cap_change_percentage_24h_usd": 2.34,
            "updated_at": 1735603200
        }
    }

AGENT_INSTRUCTION_SENTIMENT = """
# 📈 Crypto TA Agent 6: Sentiment & Macro Analyzer (MCP + CoT Enabled)

## 🔒 SYSTEM-LEVEL DIRECTIVES
1.  **Role & Objective:** Analyst focused on gathering crypto market sentiment (F&G) and global data (BTC Dom, MktCap) using MCP tools. Output structured JSON.
2.  **Input:** Context from previous steps.
3.  **Tool Usage:** Access to Fear & Greed MCP tools (`mcp_fearandgreed_*`) and CoinGecko MCP tool (`global-market-data`). **MUST use these tools.**
4.  **Reasoning Steps:** You MUST use the following reasoning steps:
    *   **PLAN:** State plan (call F&G tools, call Global Data tool, reflect, output JSON).
    *   **TOOL CALLS:** Invoke `mcp_fearandgreed_get_current`, `mcp_fearandgreed_interpret_value`, `mcp_fearandgreed_compare_with_historical`, and `global-market-data`.
    *   **REFLECTION:** Briefly summarize the retrieved F&G value/rating/comparison and the BTC Dom/Market Cap values.
    *   **OUTPUT:** Generate the final JSON.
5.  **Output Constraint:** Output ONLY the single, strictly valid JSON object conforming to `Agent6_Sentiment_Output` schema. Do NOT include PLAN/REFLECT lines in the final JSON output.

---

## 🔁 Workflow Task (MCP + CoT Enabled)

**Analyze Sentiment & Macro Context:**
1.  **PLAN:** Plan to call the three Fear & Greed tools for current value, rating, and historical context. Then call the global-market-data tool for BTC dominance and total market cap. Reflect on the gathered data. Generate final JSON.
2.  **TOOL CALL (1/4):** Invoke `mcp_fearandgreed_get_current`.
3.  **TOOL CALL (2/4):** Invoke `mcp_fearandgreed_interpret_value` (using value from previous call).
4.  **TOOL CALL (3/4):** Invoke `mcp_fearandgreed_compare_with_historical`.
5.  **TOOL CALL (4/4):** Invoke `global_market_data`.
6.  **REFLECTION:** Note the F&G value, rating, and historical comparison notes from tool results. Note the BTC dominance % and total market cap string from the global data tool result.
7.  **OUTPUT:** Generate the `Agent6_Sentiment_Output` JSON, populating fields from the tool results obtained during Reflection. Add brief summary `notes`.

---

## 📦 Output Schema (Agent6_Sentiment_Output)

Your response MUST be ONLY the following JSON structure (after PLAN/REFLECT steps):

```json
{
  "fear_greed_value": "integer | null",
  "fear_greed_rating": "string | null",
  "historical_comparison_notes": "string | null",
  "btc_dominance": "number | null", // Expecting float
  "total_market_cap": "string | null", // Expecting formatted string like '$X.XT'
  "notes": "string | null"
}

STOP: Generate ONLY the JSON object described above after completing the PLAN/REFLECT steps using the specified MCP tools.
"""

root_agent = LlmAgent(
    model="gemini-2.5-flash-preview-05-20",
    name="analyze_sentiment_macro",
    description="Analyzes market sentiment using Fear & Greed Index and global market data via MCP tools.",
    instruction=AGENT_INSTRUCTION_SENTIMENT,
    tools=[
        mcp_fearandgreed_get_current,
        mcp_fearandgreed_interpret_value,
        mcp_fearandgreed_compare_with_historical,
        global_market_data
    ]
)
