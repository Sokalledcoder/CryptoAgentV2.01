from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Define the Pydantic model for the output schema
class Agent9_ConfidenceRisk_Output(BaseModel):
    winProbability: Optional[int] = Field(None, description="Heuristic win probability score (0-100)")
    confidence_pct: Optional[int] = Field(None, description="Confidence percentage, potentially same as winProbability")
    risk_pct: Optional[float] = Field(None, description="Recommended risk percentage (0.5, 1.0, 1.5, 2.0)")
    confidence_tier: Optional[str] = Field(None, description="Qualitative confidence tier (high, medium, low)")
    reasoning: Optional[str] = Field(None, description="Justification for WP and confidence tier based on weighted assessment")
    notes: Optional[str] = Field(None, description="Additional notes or observations")

from google.adk.agents import LlmAgent # Corrected import
import json

class ConfidenceRiskAgent(LlmAgent): # Inherit from LlmAgent
    def __init__(self):
        super().__init__(
            model="gemini-2.5-flash-preview-05-20", # Added model
            name="ConfidenceRiskAssessor",
            description="Evaluates overall technical picture, calculates Win Probability (WP), and assigns Confidence tier and Risk budget.",
            output_schema=Agent9_ConfidenceRisk_Output, # Added output_schema
            tools=[] # No external tools for this agent
        )

    async def run(self, context_from_previous_agents: Dict[str, Any]) -> Agent9_ConfidenceRisk_Output:
        # PLAN: Review all context A1-A8, A5b. Determine overall potential directional bias.
        # Calculate WP score based on weighted factor alignment with this bias.
        # Apply RR penalty if applicable. Determine Confidence tier & Risk % based on WP and Agent 8's setup.
        print("PLAN: Reviewing context from Agents 1-8 to assess overall bias. Calculating Win Probability based on weighted factors. Determining Confidence tier and Risk percentage.")
        print(f"Context from previous agents: {json.dumps(context_from_previous_agents, indent=2)}")

        # Simulate extracting relevant data and a hypothetical RR value
        # In a real scenario, this would involve parsing the complex JSON structure
        # from context_from_previous_agents.
        
        # Dummy values for simulation
        potential_direction = "long" # Assume a bullish bias from previous agents
        agent8_direction = context_from_previous_agents.get('step08_tradesetup', {}).get('direction')
        simulated_rr_value = 3.0 # Assume a good RR for now

        # B. Calculate Score (Start at 50%)
        wp_score = 50
        reasoning_factors = []

        # Simulate points based on hypothetical strong alignment
        # Structure (A2 - 15pts)
        wp_score += 15
        reasoning_factors.append("Strong bullish market structure (+15)")

        # Liquidity (A4 - 20pts)
        wp_score += 20
        reasoning_factors.append("Key demand zones holding, indicating strong liquidity support (+20)")

        # Momentum (A5 - 15pts)
        wp_score += 10 # Slightly less than max for variety
        reasoning_factors.append("Momentum indicators showing strong bullish trend (+10)")

        # Derivatives (A5b - 15pts)
        wp_score += 12 # Slightly less than max for variety
        reasoning_factors.append("Derivatives (OI, Funding, CVD) confirming bullish bias (+12)")

        # Ranges (A3 - 10pts)
        wp_score += 8
        reasoning_factors.append("Price interacting positively with predictive ranges (+8)")

        # Sentiment/Macro (A6 - 5pts)
        wp_score += 3
        reasoning_factors.append("Overall sentiment leaning positive (+3)")

        # News (A7 - 5pts)
        wp_score += 3
        reasoning_factors.append("Recent news generally positive for asset (+3)")

        # C. Apply RR Penalty (Conditional)
        if agent8_direction and simulated_rr_value is not None and simulated_rr_value < 2.0:
            wp_score -= 20
            reasoning_factors.append("RR penalty applied due to low RR (<2.0) (-20)")

        # D. Final Score: Cap between 0 and 100
        win_probability = max(0, min(100, wp_score))

        # E. Determine Confidence Tier & Risk %
        confidence_tier = None
        risk_pct = None
        confidence_pct = win_probability # For now, confidence_pct is same as WP

        if win_probability > 70 and agent8_direction is not None and simulated_rr_value >= 2.0:
            confidence_tier = "high"
            risk_pct = 1.5
        elif 55 <= win_probability <= 70 and agent8_direction is not None:
            confidence_tier = "medium"
            risk_pct = 1.0
        else:
            confidence_tier = "low"
            risk_pct = 0.5
            if agent8_direction is None:
                reasoning_factors.append("No immediate setup proposed by Agent 8, limiting confidence for action.")

        # F. Reasoning
        final_reasoning = f"Win Probability of {win_probability}% derived from: {'; '.join(reasoning_factors)}. Confidence is {confidence_tier} due to high WP and a valid Agent 8 setup with acceptable RR."
        if agent8_direction is None:
             final_reasoning = f"Win Probability of {win_probability}% derived from: {'; '.join(reasoning_factors)}. Confidence is {confidence_tier} as no immediate setup was proposed by Agent 8, despite high WP."


        # REFLECTION: State the final calculated winProbability, confidence_tier, and risk_pct.
        print(f"REFLECTION: Calculated Win Probability: {win_probability}%. Confidence Tier: {confidence_tier}. Recommended Risk: {risk_pct}%.")
        print(f"Reasoning: {final_reasoning}")

        # OUTPUT: Generate the Agent9_ConfidenceRisk_Output JSON
        return Agent9_ConfidenceRisk_Output(
            winProbability=win_probability,
            confidence_pct=confidence_pct,
            risk_pct=risk_pct,
            confidence_tier=confidence_tier,
            reasoning=final_reasoning,
            notes="This is a simulated output. Actual calculation requires full integration of previous agent outputs and real RR value."
        )
