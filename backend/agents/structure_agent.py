from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# 1. Define Pydantic Models for Output Schema (v13)
class MajorSwing(BaseModel):
    type: Literal["HH", "LL", "LH", "HL"]

class BosEvent(BaseModel):
    type: Optional[Literal["BOS_up", "BOS_down"]] = None
    position: Optional[Literal["above", "below", "at"]] = None

class ChochEvent(BaseModel):
    type: Optional[Literal["CHoCH_up", "CHoCH_down"]] = None
    position: Optional[Literal["above", "below", "at"]] = None

class MondayStatus(BaseModel):
    high: Literal["above", "below", "at", "inside"]
    low: Literal["above", "below", "at", "inside"]

class Agent2_Structure_Output(BaseModel):
    structure_phase: Optional[Literal["accumulation", "distribution", "trend_up", "trend_down", "ranging"]] = None
    major_swings: List[MajorSwing] = Field(default_factory=list)
    bos_event: BosEvent = Field(default_factory=BosEvent)
    choch_event: ChochEvent = Field(default_factory=ChochEvent)
    monday_status: MondayStatus
    notes: Optional[str] = None

AGENT_INSTRUCTION_STRUCTURE = """
# 📈 Crypto TA Agent 2 – Market Structure & Monday Range
*(v13 — Visual Spatial Comparison, Relative Position Only)*

## 🔒 SYSTEM-LEVEL DIRECTIVES
1.  **Role & Objective**
    Act as an expert chart analyst focusing on **visual spatial comparison** to determine relative positioning. Output **only**:
    *   Overall market **structure_phase**.
    *   Optional: The **type** of the last major High and Low (`major_swings` list - type only, NO PRICES).
    *   The **type** and **relative position** (result of comparing latest candle close **vertically** against the signal's line) of the **single most-recent visible** AlgoAlpha **BOS event**.
    *   The **type** and **relative position** (result of comparing latest candle close **vertically** against the signal's line) of the **single most-recent visible** AlgoAlpha **CHoCH event**.
    *   The **relative status** (result of comparing latest candle close **vertically** against the specific lines) of the current price compared to the **dotted, right-anchored lines *labeled* 'Monday High'/'Monday Low'**.
    *   Brief free-text notes with source tags.
    **ABSOLUTELY FORBIDDEN IN FINAL JSON:** Numeric prices for BOS/CHoCH events or Monday levels/status. Keys like `price_level`, `monday_high`, `monday_low`. Use **ONLY** the keys defined in the v13 schema below. Do **NOT** use OCR to extract numbers for position/status determination; use **visual comparison only**.

2.  **Tools / RAG**
    Query file_search_tool for context: AlgoAlpha definitions, Monday Range strategy/bias, Swing Point definitions, SpacemanBTC Monday plotting/visibility rules.

3.  **Visual keys (Reminder)**
    *   AlgoAlpha: Labels "BOS"/"CHoCH". Compare price position **vertically** against the label's **horizontal line**.
    *   Monday Range: **Dotted** lines on **right**. Find lines with **exact label text** "Monday High" / "Monday Low". Compare price position **vertically** against these specific lines. **IGNORE** Weekly Open, Daily Open, etc.

4.  **Fail-fast rule (Mandatory Adherence - CHECK BEFORE OUTPUT)**
    *   Before generating the final output, **meticulously check** if your planned JSON contains **ANY key not listed in the v13 schema** OR **ANY numeric value (even null) in any field EXCEPT `major_swings.price` (which is forbidden anyway)**.
    *   If **ANY** violation is found, **YOU MUST DISCARD YOUR JSON AND RESPOND *ONLY* WITH:**
        ```json
        {"error":"SCHEMA_VIOLATION"}
        ```
    *   Only proceed to output the main JSON if it is **PERFECTLY** compliant.

---

## 🔁 WORKFLOW (Chain-of-Thought steps)

1.  **PLAN:** Query RAG; Visual analysis for latest AlgoAlpha signal (type & **spatial position**), major swings (type only), Monday lines (**spatial status**); Determine phase; Pre-computation for Reflection; Reflect; Final Schema Check; Output.
2.  **EXECUTE RAG & VISUAL ANALYSIS**
    *   Run RAG queries.
    *   **AlgoAlpha BOS:** Visually find **most recent** BOS label/line. Determine `type`. Compare latest close **vertically** to line -> `position` ("above", "below", "at"). Record `bos_event` (or nulls).
    *   **AlgoAlpha CHoCH:** Visually find **most recent** CHoCH label/line. Determine `type`. Compare latest close **vertically** to line -> `position` ("above", "below", "at"). Record `choch_event` (or nulls).
    *   **Major Swings:** Visually find last major High/Low. Record `type` only for `major_swings`.
    *   **Monday Range:** Visually find **dotted lines on right with EXACT labels "Monday High" / "Monday Low"**. Compare latest close **vertically** to High line -> `status` ("above", "below", "at", or "inside" if line not visible). Compare latest close **vertically** to Low line -> `status` ("above", "below", "at", or "inside" if line not visible). Record `monday_status`.
3.  **REFLECTION**
    *   Summarize RAG.
    *   **Declare Output Values (Spatial):** State the determined values based on visual comparison:
        *   `bos_event.type = ...`, `bos_event.position = ...` (or nulls)
        *   `choch_event.type = ...`, `choch_event.position = ...` (or nulls)
        *   `monday_status.high = ...`, `monday_status.low = ...`
    *   Determine `structure_phase` based on major swings.
    *   Prepare `notes`. Include Monday bias interpretation if deviation/reclaim occurred based on `monday_status`.
    *   **Confirm Schema Compliance:** Verify prepared data uses *only* allowed keys and avoids forbidden numeric types/keys for events/ranges.
4.  **OUTPUT:**
    *   **Apply Mandatory Fail-fast rule check.** If violation detected, output schema violation error.
    *   If compliant, emit the single JSON object conforming **EXACTLY** to the v13 schema below.
    *   *No PLAN / EXECUTE / REFLECTION prose.*

---

## 📦 OUTPUT SCHEMA (v13 - Ultra Strict Relative Position) - Defined as Pydantic Model

Your response MUST be ONLY the following JSON structure (or the SCHEMA_VIOLATION error).

STOP – After completing PLAN → EXECUTE → REFLECTION, output only the JSON object above (or the SCHEMA_VIOLATION object).
ABSOLUTELY NO numeric fields for BOS/CHoCH events or Monday status/levels. Focus on correct spatial determination of above/below/at/inside. Ensure perfect schema compliance.
"""

class StructureAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash-preview-05-20", # Assuming vision capabilities
            name="analyze_market_structure",
            description="Analyzes market structure, AlgoAlpha signals, and Monday Range positioning using visual spatial comparison.",
            instruction=AGENT_INSTRUCTION_STRUCTURE,
            output_schema=Agent2_Structure_Output
        )

        search_tool = FunctionTool(func=self._simulated_file_search)
        search_tool.name = "file_search_tool"
        search_tool.description = "Simulates a RAG/FileSearch tool for querying knowledge base about AlgoAlpha definitions, Monday Range strategy, Swing Point definitions, etc."
        search_tool.input_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query for the knowledge base."}
            },
            "required": ["query"]
        }
        self.tools: List[FunctionTool] = [search_tool]

    async def _simulated_file_search(self, query: str) -> dict:
        """
        Simulates a RAG/FileSearch tool for querying knowledge base.
        """
        print(f"[StructureAgent Tool SIMULATION] _simulated_file_search called with query: {query}")
        
        query_lower = query.lower()
        if "algolpha" in query_lower or "bos" in query_lower or "choch" in query_lower:
            return {
                "results": [
                    {
                        "content": "AlgoAlpha BOS (Break of Structure) indicates a bullish or bearish break. CHoCH (Change of Character) indicates trend reversal. Both are marked with horizontal lines at the break level.",
                        "source": "AlgoAlpha_definitions.md"
                    }
                ]
            }
        elif "monday" in query_lower:
            return {
                "results": [
                    {
                        "content": "Monday Range strategy uses dotted lines labeled 'Monday High' and 'Monday Low' on the right side of the chart. Price above Monday High suggests bullish bias, below Monday Low suggests bearish bias.",
                        "source": "Monday_Range_strategy.md"
                    }
                ]
            }
        elif "swing" in query_lower:
            return {
                "results": [
                    {
                        "content": "Swing points: HH (Higher High), LL (Lower Low), LH (Lower High), HL (Higher Low). Used to determine market structure phases.",
                        "source": "Swing_Point_definitions.md"
                    }
                ]
            }
        else:
            return {
                "results": [
                    {
                        "content": "General market structure analysis involves identifying trend phases, swing points, and key levels.",
                        "source": "General_TA.md"
                    }
                ]
            }
