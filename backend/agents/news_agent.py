from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import re # For date extraction

# Define the Pydantic model for the output schema
class Agent7_News_Output(BaseModel):
    general_market_news: Optional[List[str]] = Field(None, description="Concise summaries of relevant key sentiment drivers for the general market")
    asset_specific_news: Optional[List[str]] = Field(None, description="Concise summaries of relevant price-relevant points for the specific asset")
    weekly_summary: Optional[str] = Field(None, description="Summary of major crypto market themes from the previous week")
    market_news_sentiment: Optional[str] = Field(None, description="Overall sentiment of general market news (Positive, Negative, Neutral, Mixed)")
    asset_news_sentiment: Optional[str] = Field(None, description="Overall sentiment of asset-specific news (Positive, Negative, Neutral, Mixed)")
    notes: Optional[str] = Field(None, description="Additional notes, conflict warnings, or notes on irrelevant searches")

from google.adk.agents import LlmAgent
import os # For environment variables
import json # May not be needed after refactor
import re # For date extraction (if used by LLM, though prompt handles it)
from backend.tools.mcp_wrappers import PerplexityMCPTool # Import the new tool

# Define the Pydantic model for the output schema (Agent7_News_Output is already defined above)

AGENT_INSTRUCTION_NEWS = """
# 📰 Crypto TA Agent 7: News & Sentiment Analyzer (Perplexity MCP)

## 🔒 SYSTEM-LEVEL DIRECTIVES
1.  **Role & Objective:** Act as a news analyst. Your goal is to use the `call_perplexity_mcp` tool to interact with the Perplexity MCP server for gathering relevant news and sentiment.
2.  **Input:** Context from previous steps, which should include the current date and the specific asset being analyzed.
3.  **Tool Usage:** You **MUST** use the `call_perplexity_mcp` tool.
    *   This tool takes two arguments:
        1.  `tool_to_call` (string): The name of the actual Perplexity tool you want to use (e.g., "search", "chat_perplexity", "get_documentation").
        2.  `tool_args` (dict): A dictionary of arguments for that specific Perplexity tool.
    *   Example: To use Perplexity's "search" tool for "latest crypto news":
        Call `call_perplexity_mcp` with `tool_to_call="search"` and `tool_args={"query": "latest crypto market news"}`.
    *   Example: To use Perplexity's "chat_perplexity" tool:
        Call `call_perplexity_mcp` with `tool_to_call="chat_perplexity"` and `tool_args={"message": "Summarize bullish and bearish news for Bitcoin today."}`.
    *   The `call_perplexity_mcp` tool will return a JSON string as its result.
4.  **Reasoning Steps (CoT):**
    *   **PLAN:** Identify the current date and target asset from input. Plan specific Perplexity tool calls (e.g., "search" or "chat_perplexity") and their arguments for (a) general market news/sentiment, (b) asset-specific news/sentiment, and (c) a brief weekly summary.
    *   **TOOL CALLS:** Execute the planned queries by invoking `call_perplexity_mcp` with the appropriate `tool_to_call` and `tool_args` for each query.
    *   **REFLECTION:** Parse the JSON string responses from each `call_perplexity_mcp` invocation. Evaluate relevance and content. Extract key news points and determine overall sentiment (Positive, Negative, Neutral, Mixed) for both general market and asset-specific news.
    *   **OUTPUT:** Generate the final JSON object conforming to the `Agent7_News_Output` schema.
5.  **Output Constraint:** Output ONLY the single, strictly valid JSON object. Do NOT include PLAN/REFLECT lines in the final JSON output.

---

## 🔁 Workflow Task (Perplexity MCP + CoT Enabled)

**Analyze News & Sentiment:**
1.  **PLAN:**
    *   Extract `current_date` and `base_asset_name` from the provided context.
    *   Plan to call `call_perplexity_mcp` for general market news (e.g., using Perplexity's "search" tool with a query relevant to `current_date`).
    *   Plan to call `call_perplexity_mcp` for asset-specific news (e.g., using Perplexity's "search" tool with a query for `base_asset_name` relevant to `current_date`).
    *   Plan to call `call_perplexity_mcp` for a weekly summary (e.g., using Perplexity's "search" or "chat_perplexity" tool for themes from the previous week relative to `current_date`).
2.  **TOOL CALL (General Market News):** Invoke `call_perplexity_mcp` with `tool_to_call` (e.g., "search") and appropriate `tool_args` for general market news.
3.  **REFLECTION (General Market News):** Parse the returned JSON string. Summarize relevant key points. Determine `market_news_sentiment`.
4.  **TOOL CALL (Asset-Specific News):** Invoke `call_perplexity_mcp` with `tool_to_call` (e.g., "search") and appropriate `tool_args` for asset-specific news.
5.  **REFLECTION (Asset-Specific News):** Parse the returned JSON string. Summarize relevant key points. Determine `asset_news_sentiment`.
6.  **TOOL CALL (Weekly Summary):** Invoke `call_perplexity_mcp` with `tool_to_call` (e.g., "search" or "chat_perplexity") and appropriate `tool_args` for the weekly summary.
7.  **REFLECTION (Weekly Summary):** Parse the returned JSON string. Extract the `weekly_summary`.
8.  **OUTPUT:** Generate the `Agent7_News_Output` JSON, populating all fields based on the reflections. Include any necessary `notes` (e.g., if searches were irrelevant or yielded no significant info).

---

## 📦 Output Schema (Agent7_News_Output) - Already Defined

Your response MUST be ONLY the JSON object.
STOP: Generate ONLY the JSON object.
"""

class NewsAgent(LlmAgent):
    def __init__(self):
        # Instantiate the custom PerplexityMCPTool
        # The tool itself handles PERPLEXITY_API_KEY from os.environ internally when it runs.
        pplx_tool = PerplexityMCPTool()

        super().__init__(
            model="gemini-1.5-flash-latest", 
            name="NewsAnalyzer",
            description="Researches and analyzes crypto news using the Perplexity MCP wrapper tool.",
            instruction=AGENT_INSTRUCTION_NEWS, # Use the updated instruction
            tools=[pplx_tool], # Use the custom FunctionTool wrapper
            output_schema=Agent7_News_Output
        )
        # The LlmAgent will use the `call_perplexity_mcp` tool based on the updated prompt.
