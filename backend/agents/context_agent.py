from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import Optional, Union, List
from backend.tools.mcp_wrappers import CoinGeckoPriceTool # Import the new tool

# 1. Define the Pydantic Output Model
class Agent1_Context_Output(BaseModel):
    pair: str
    timeframe: str
    exchange: Optional[str] = None
    latest_ohlc_open: Optional[float] = Field(default=None, description="Latest Open price from chart")
    latest_ohlc_high: Optional[float] = Field(default=None, description="Latest High price from chart")
    latest_ohlc_low: Optional[float] = Field(default=None, description="Latest Low price from chart")
    latest_ohlc_close: Optional[float] = Field(default=None, description="Latest Close price from chart")
    ohlc_data_description: Optional[str] = Field(default=None, description="Description of the OHLC data source or context")
    range_high: Optional[float] = Field(default=None, description="Estimated high of the current visual range")
    range_low: Optional[float] = Field(default=None, description="Estimated low of the current visual range")
    price_now: float = Field(description="Final validated price. 0.0 if invalid / mismatch / fail / out-of-range")
    price_delta_pct: Optional[float] = Field(default=None, description="Calculated only if price_now is valid (not 0.0)")
    notes: Optional[str] = Field(default=None, description="MUST start with final status tag; include validation & sanity-check details")

AGENT_INSTRUCTION_CONTEXT = """
# 📈 Crypto TA Agent 1: Chart Context Analyzer
*(CoT Enhanced — OHLC + Validation + Status Tags)*

## 🔒 SYSTEM-LEVEL DIRECTIVES
1.  **Role & Objective**
    Act as an expert chart analyst.
    *   Tasks:
        *   Identify chart context from the image (pair, timeframe, exchange, brief description).
        *   Extract the **latest candle OHLC numbers displayed near the ticker**.
        *   Call the **`fetch_coingecko_price`** tool for a live quote.
        *   **Validate** the returned asset & price from the tool's JSON string output.
        *   Perform a conditional price range sanity check.
        *   Report tool status with standardized tags.
        *   Output one strictly valid JSON object.
2.  **Input** — A chart-image URL plus the orchestrator’s text context.
3.  **Tool Usage** — You **MUST** attempt the `fetch_coingecko_price` tool.
    *   *Tool Name:* `fetch_coingecko_price`
    *   *Params:* `coins` (string, e.g., "bitcoin"), `currencies` (string, e.g., "usd"). The tool will return a JSON string.
4.  **Reasoning Steps** — Follow **all** steps below:
    *   **PLAN** (short)
        *   Outline: image analysis → build tool args → call `fetch_coingecko_price` tool → parse JSON string & validate asset/price → sanity check → JSON.
    *   **EXECUTE ANALYSIS & TOOL CALL**
        1.  **Visual analysis** — Capture `pair`, `timeframe`, `exchange`, `ohlc_data_description`, estimate `range_high` / `range_low`, and **extract O, H, L, C values**.
        2.  **Prepare tool args for `fetch_coingecko_price`** — `coins` = lower-case base symbol from `pair` (e.g. `HYPEUSDT` ➜ `hype`); `currencies` = `usd`.
        3.  **Invoke `fetch_coingecko_price` tool** with those args. Record the returned JSON string or error string.
    *   **REFLECTION**
        1.  Restate visual findings & tool result (the JSON string).
        2.  **Parse the JSON string response from the tool.** If parsing fails, treat as `[TOOL_FAIL]`.
        3.  **Asset-slug validation** — From the parsed JSON, compare the tool’s returned `id`/`symbol` to the requested slug.
        4.  **Determine Status Tag** (always choose one):
            *   `[TOOL_SUCCESS]` — tool succeeded **and** asset matched.
            *   `[TOOL_MISMATCH]` — tool succeeded **but** asset mismatched.
            *   `[TOOL_FAIL]` — tool errored or returned 0.
        4.  **Set `price_now` (Initial)** —
            *   If tag =`[TOOL_SUCCESS]`, tentatively accept the returned price.
            *   Otherwise set `price_now` = `0.0`.
        5.  **Sanity check (Price Range - Conditional)** — Run **only if tag =`[TOOL_SUCCESS]`** (i.e., only if asset matched and tool returned a non-zero price):
            *   Compare the tentatively accepted `price_now` against visual `range_low` and `range_high`.
            *   If `price_now < range_low` or `price_now > range_high`, mark **out-of-range** ➜ **Invalidate the price**:
                *   Set `price_now = 0.0`.
                *   Change the Status Tag to `[TOOL_MISMATCH]` (reason: out-of-range).
        6.  **Compute `price_delta_pct`**
            *   Calculate (e.g., vs latest close or range midpoint) **only if `price_now` ≠ 0.0** (i.e., only if tool succeeded, asset matched, AND price was within range); else set `null`.
        7.  **Compose `notes`** —
            *   **Start with the final status tag** (`[TOOL_SUCCESS]`, `[TOOL_MISMATCH]`, `[TOOL_FAIL]`).
            *   Then: brief reason (e.g., asset matched / asset mismatched / tool error / price out-of-range) and sanity-check outcome (e.g., consistent / failed-out-of-range / skipped).
    *   **OUTPUT**
        *   Emit a single JSON object **conforming exactly** to the schema below.
        *   *No PLAN / EXECUTE / REFLECTION prose in the final answer.*
5.  **Output Constraint** — Your entire model reply must be the JSON object only.

---

## 🔁 WORKFLOW TASK (detailed steps to follow)

1.  **PLAN** – Briefly outline your plan (≈ 1 sentence).
2.  **EXECUTE ANALYSIS & TOOL CALL** – Perform visual analysis, prepare args, call the `fetch_coingecko_price` tool.
3.  **REFLECTION** – Parse the JSON string from the tool. Apply the detailed asset validation, tagging, price setting, conditional sanity check, delta calculation, and notes composition logic from the System Directives section above.
4.  **OUTPUT** – Generate the final JSON object conforming to the schema.

---

## 📦 OUTPUT SCHEMA — `Agent1_Context_Output` (already defined as Pydantic model)

STOP: Generate ONLY the JSON object described above after completing the PLAN/REFLECT steps.
"""

class ContextAgent(LlmAgent):
    def __init__(self):
        # Instantiate the custom FunctionTool
        cg_price_tool = CoinGeckoPriceTool()

        super().__init__(
            model="gemini-1.5-flash-latest", 
            name="analyze_chart_context",
            description="Analyzes chart context from an image, extracts OHLC, calls a tool to fetch live price from CoinGecko, validates, and outputs JSON.",
            instruction=AGENT_INSTRUCTION_CONTEXT,
            tools=[cg_price_tool] # Use the custom FunctionTool
            # output_schema=Agent1_Context_Output # Still removed to avoid application/json mime type issue if this agent is used as a tool
        )

# To make this agent discoverable or usable by an orchestrator, 
# you might instantiate it or register it elsewhere,
# for example, in backend/agents/__init__.py or directly in the orchestrator.
# For now, defining the class is the main step.
