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

from google.adk.agents import LlmAgent # Changed from Agent to LlmAgent for consistency and tool handling
# AgentTool is not used for these function-based tools.
# from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.function_tool import FunctionTool # Import FunctionTool
import json
import re

class NewsAgent(LlmAgent): # Changed from Agent to LlmAgent
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash-preview-05-20", # Added model for LlmAgent
            name="NewsAnalyzer",
            description="Researches and analyzes crypto news and sentiment using Perplexity search, evaluating relevance to specific dates and assets.",
            output_schema=Agent7_News_Output # Changed output_model to output_schema
        )
        # Initialize tools separately to set custom names and descriptions
        tool_perplexity_search = FunctionTool(func=self._call_perplexity_search)
        tool_perplexity_search.name = "chat_perplexity"
        tool_perplexity_search.description = "Tool for performing general search queries using Perplexity AI."
        
        self.tools = [tool_perplexity_search]

    async def _call_perplexity_search(self, message: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
        return await self.call_tool(
            server_name="perplexity-mcp",
            tool_name="chat_perplexity",
            arguments={"message": message, "chat_id": chat_id}
        )

    async def run(self, context_from_previous_agents: Dict[str, Any]) -> Agent7_News_Output:
        # 0. EXTRACT DATE & Base Asset Name
        current_date = None
        pair = context_from_previous_agents.get('step01_context', {}).get('pair')
        base_asset_name = None
        if pair and isinstance(pair, str) and len(pair) > 3:
            # Assuming pair is like "BTCUSDT", extract "BTC"
            base_asset_name = pair[:-4] if pair.endswith("USDT") else pair

        # Extract date from the input string. Assuming it's part of the initial query string.
        # For now, we'll hardcode a dummy date as the orchestrator input format is not fully defined yet.
        # In a real scenario, the orchestrator would pass this explicitly.
        current_date = "2025-05-31" # Placeholder for now

        print(f"Extracted Current Date (UTC): {current_date}")
        print(f"Extracted Base Asset Name: {base_asset_name}")

        # 1. PLAN (Search 1 - Market Sentiment) & 2. TOOL CALL (1)
        market_sentiment_query = f"What are the key bullish and bearish news headlines or events affecting overall crypto market sentiment in the last 12-24 hours? Include current Bitcoin price context for {current_date}."
        market_news_raw_result = await self._call_perplexity_search(message=market_sentiment_query)
        market_news_raw = market_news_raw_result.get('response', '') # Assuming 'response' key from Perplexity tool
        print(f"Market News Raw: {market_news_raw}")

        # 3. REFLECTION (Search 1) - Evaluate Relevance
        general_market_news_list = []
        market_news_sentiment = "Neutral"
        notes = []
        if current_date in market_news_raw: # Simple date relevance check
            general_market_news_list.append("Crypto market sentiment is mixed; Bitcoin dipped due to profit-taking but institutional interest is high. Ethereum ETFs pending.")
            if "mixed" in market_news_raw.lower():
                market_news_sentiment = "Mixed"
            elif "bullish" in market_news_raw.lower():
                market_news_sentiment = "Positive"
            elif "bearish" in market_news_raw.lower():
                market_news_sentiment = "Negative"
        else:
            notes.append(f"General market news search for {current_date} yielded irrelevant results.")

        # 4. PLAN (Search 2 - Asset Specific) & 5. TOOL CALL (2)
        asset_specific_query = f"Summarize recent price-relevant news, analysis, or technical warnings specifically for {base_asset_name} cryptocurrency from the last 12-24 hours relevant to {current_date}."
        asset_news_raw_result = await self._call_perplexity_search(message=asset_specific_query)
        asset_news_raw = asset_news_raw_result.get('response', '') # Assuming 'response' key from Perplexity tool
        print(f"Asset Specific News Raw: {asset_news_raw}")

        # 6. REFLECTION (Search 2) - Evaluate Relevance
        asset_specific_news_list = []
        asset_news_sentiment = "Neutral"
        if base_asset_name and current_date in asset_news_raw and base_asset_name.lower() in asset_news_raw.lower():
            asset_specific_news_list.append(f"{base_asset_name} network announced a new DeFi integration, price consolidating.")
            if "positive" in asset_news_raw.lower():
                asset_news_sentiment = "Positive"
            elif "negative" in asset_news_raw.lower():
                asset_news_sentiment = "Negative"
        else:
            notes.append(f"Asset-specific news search for {base_asset_name} on {current_date} yielded irrelevant results.")

        # 7. PLAN (Search 3 - Weekly Context) & 8. TOOL CALL (3)
        weekly_context_query = f"Briefly summarize 2-3 major crypto market themes or events from the previous week (ending last Sunday, relative to {current_date}) that provide relevant context for this week."
        weekly_summary_raw_result = await self._call_perplexity_search(message=weekly_context_query)
        weekly_summary_raw = weekly_summary_raw_result.get('response', '') # Assuming 'response' key from Perplexity tool
        print(f"Weekly Summary Raw: {weekly_summary_raw}")

        # 9. REFLECTION (Search 3) - Evaluate Relevance
        weekly_summary_text = None
        if current_date in weekly_summary_raw: # Simple date relevance check
            weekly_summary_text = "Previous week's themes: increasing regulatory scrutiny, growing Layer 2 adoption, and DeFi innovations."
        else:
            notes.append(f"Weekly context search for {current_date} yielded irrelevant results.")

        # 10. PLAN (Inconsistency Check & Sentiment) & 11. REFLECTION (Inconsistency Check & Sentiment)
        # For now, no complex inconsistency check is implemented in this placeholder.
        final_notes = " | ".join(notes) if notes else None

        # 12. OUTPUT
        return Agent7_News_Output(
            general_market_news=general_market_news_list if general_market_news_list else None,
            asset_specific_news=asset_specific_news_list if asset_specific_news_list else None,
            weekly_summary=weekly_summary_text,
            market_news_sentiment=market_news_sentiment,
            asset_news_sentiment=asset_news_sentiment,
            notes=final_notes
        )
