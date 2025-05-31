from google.adk.agents import LlmAgent
from typing import Dict, Any # May not be needed after refactor
from backend.tools.mcp_wrappers import ( # Import new tools
    FearAndGreed_GetCurrentTool,
    FearAndGreed_InterpretValueTool,
    FearAndGreed_CompareHistoricalTool,
    CoinGecko_GlobalMarketDataTool
)
# Define the Pydantic model for the output schema
from pydantic import BaseModel, Field
from typing import Optional

class Agent6_Sentiment_Output(BaseModel):
    fear_greed_value: Optional[int] = Field(None, description="Fear and Greed Index value")
    fear_greed_rating: Optional[str] = Field(None, description="Fear and Greed Index rating")
    historical_comparison_notes: Optional[str] = Field(None, description="Notes on historical comparison of Fear and Greed Index")
    btc_dominance: Optional[float] = Field(None, description="Bitcoin Dominance percentage")
    total_market_cap: Optional[str] = Field(None, description="Total crypto market capitalization")
    notes: Optional[str] = Field(None, description="Additional notes or observations")

class SentimentAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash-preview-05-20",
            name="analyze_sentiment_macro",
            description="Analyzes market sentiment using Fear & Greed Index and global market data via MCP tools.",
            instruction="""
# 📈 Crypto TA Agent 6: Sentiment & Macro Analyzer (MCP + CoT Enabled)

## 🔒 SYSTEM-LEVEL DIRECTIVES
1.  **Role & Objective:** Analyst focused on gathering crypto market sentiment (F&G) and global data (BTC Dom, MktCap) using specific wrapper tools. Output structured JSON.
2.  **Input:** Context from previous steps.
3.  **Tool Usage:** You have access to the following tools:
    *   `fetch_fearandgreed_current`: Gets current F&G value.
    *   `interpret_fearandgreed_value`: Interprets an F&G value.
    *   `compare_fearandgreed_historical`: Compares F&G to historical data.
    *   `fetch_coingecko_global_market_data`: Gets BTC dominance and total market cap.
    **MUST use these tools.**
4.  **Reasoning Steps:** You MUST use the following reasoning steps:
    *   **PLAN:** State plan (call F&G tools, call Global Data tool, reflect, output JSON).
    *   **TOOL CALLS:** Invoke `fetch_fearandgreed_current`, then `interpret_fearandgreed_value` (with the value from the first call), then `compare_fearandgreed_historical`, and finally `fetch_coingecko_global_market_data`.
    *   **REFLECTION:** Briefly summarize the retrieved F&G value/rating/comparison and the BTC Dom/Market Cap values from the JSON string responses of the tools.
    *   **OUTPUT:** Generate the final JSON.
5.  **Output Constraint:** Output ONLY the single, strictly valid JSON object conforming to `Agent6_Sentiment_Output` schema. Do NOT include PLAN/REFLECT lines in the final JSON output.

---

## 🔁 Workflow Task (MCP + CoT Enabled)

**Analyze Sentiment & Macro Context:**
1.  **PLAN:** Plan to call `fetch_fearandgreed_current`, then `interpret_fearandgreed_value`, then `compare_fearandgreed_historical`, and `fetch_coingecko_global_market_data`. Reflect on the gathered data from their JSON string responses. Generate final JSON.
2.  **TOOL CALL (1/4):** Invoke `fetch_fearandgreed_current`.
3.  **TOOL CALL (2/4):** Invoke `interpret_fearandgreed_value` (using value from the JSON string response of the previous call).
4.  **TOOL CALL (3/4):** Invoke `compare_fearandgreed_historical`.
5.  **TOOL CALL (4/4):** Invoke `fetch_coingecko_global_market_data`.
6.  **REFLECTION:** Parse the JSON string responses from each tool. Note the F&G value, rating, and historical comparison notes. Note the BTC dominance % and total market cap string.
7.  **OUTPUT:** Generate the `Agent6_Sentiment_Output` JSON, populating fields from the parsed tool results obtained during Reflection. Add brief summary `notes`.

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
""",
            output_schema=Agent6_Sentiment_Output # Output schema remains the same
        )
        
        # Instantiate the custom FunctionTool wrappers
        fg_current_tool = FearAndGreed_GetCurrentTool()
        fg_interpret_tool = FearAndGreed_InterpretValueTool()
        fg_compare_tool = FearAndGreed_CompareHistoricalTool()
        cg_global_data_tool = CoinGecko_GlobalMarketDataTool()

        self.tools = [
            fg_current_tool,
            fg_interpret_tool,
            fg_compare_tool,
            cg_global_data_tool
        ]
        # The LlmAgent will use these tools based on the updated prompt.

# The explicit root_agent instantiation might be for local testing or older patterns.
# We can remove it if it's not directly used by the main application flow.
# For now, let's comment it out to avoid potential side effects if this file is imported.
# root_agent = SentimentAgent()
