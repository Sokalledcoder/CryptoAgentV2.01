from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Define the Pydantic models for the output schema
class ActionStep(BaseModel):
    step_number: int = Field(..., description="Numbered step in the action plan")
    description: str = Field(..., description="Description of the action step")
    condition: Optional[str] = Field(None, description="Condition for executing this step")

class InvalidationTrigger(BaseModel):
    type: str = Field(..., description="Type of invalidation (technical, time_based, event_based)")
    description: str = Field(..., description="Description of the invalidation trigger")
    price_level: Optional[float] = Field(None, description="Price level associated with the invalidation, if applicable")

class Agent10_ActionPlan_Output(BaseModel):
    action_plan: List[ActionStep] = Field([], description="List of action plan steps")
    invalidation_triggers: List[InvalidationTrigger] = Field([], description="List of invalidation triggers or re-analysis conditions")
    notes: Optional[str] = Field(None, description="Additional notes on the execution plan")

from google.adk.agent import Agent
import json

class ActionPlanAgent(Agent):
    def __init__(self):
        super().__init__(
            name="ActionPlanSpecialist",
            description="Defines clear action plan steps and specific invalidation triggers based on trade setup and confidence/risk assessment.",
            output_model=Agent10_ActionPlan_Output,
            tools=[] # No external tools for this agent
        )

    async def run(self, context_from_previous_agents: Dict[str, Any]) -> Agent10_ActionPlan_Output:
        # PLAN: Check if Agent 8 proposed a trade. If yes, review setup/confidence and define execution steps & invalidation triggers.
        # If no, define re-analysis triggers.
        print("PLAN: Reviewing trade setup and confidence to define actionable steps and invalidation triggers.")
        print(f"Context from previous agents: {json.dumps(context_from_previous_agents, indent=2)}")

        # Simulate extracting data from Agent 8 and Agent 9 outputs
        agent8_output = context_from_previous_agents.get('step08_tradesetup', {})
        agent9_output = context_from_previous_agents.get('step09_confidencerisk', {})

        direction = agent8_output.get('direction')
        entry = agent8_output.get('entry')
        stop = agent8_output.get('stop')
        take_profit = agent8_output.get('take_profit')
        confidence_tier = agent9_output.get('confidence_tier')

        action_plan_list: List[ActionStep] = []
        invalidation_triggers_list: List[InvalidationTrigger] = []
        notes = None

        if direction and entry and stop and take_profit:
            # Trade setup exists
            action_plan_list.append(ActionStep(step_number=1, description=f"Set limit {direction} entry order at {entry}.", condition="If price approaches the entry level."))
            action_plan_list.append(ActionStep(step_number=2, description="Monitor for price action confirmation (e.g., rejection, breakout).", condition="Upon potential entry."))
            action_plan_list.append(ActionStep(step_number=3, description=f"Place stop loss order at {stop}.", condition="Once entry is confirmed."))
            action_plan_list.append(ActionStep(step_number=4, description=f"Set take profit order at {take_profit}.", condition="Once entry is confirmed."))
            action_plan_list.append(ActionStep(step_number=5, description="Actively manage trade based on market developments and price action.", condition="During trade execution."))

            invalidation_triggers_list.append(InvalidationTrigger(type="technical", description=f"Price closes decisively beyond stop loss level {stop}.", price_level=stop))
            invalidation_triggers_list.append(InvalidationTrigger(type="time_based", description="Entry condition not met within 24 hours.", price_level=None))
            invalidation_triggers_list.append(InvalidationTrigger(type="event_based", description="Major unexpected news event contradicting the trade bias.", price_level=None))
            notes = f"Execution plan for a {direction} trade with {confidence_tier} confidence. Focus on confirmation and strict risk management."
        else:
            # No trade setup
            action_plan_list = []
            invalidation_triggers_list.append(InvalidationTrigger(type="re_analysis", description="Re-analyze if market structure changes significantly.", price_level=None))
            invalidation_triggers_list.append(InvalidationTrigger(type="re_analysis", description="Re-analyze if new liquidity zones form or are tested.", price_level=None))
            notes = "No high-probability trade setup identified at this time. Re-analysis conditions provided."

        # REFLECTION: Summarize the generated action steps and invalidation triggers (or the re-analysis triggers if no trade).
        print("REFLECTION: Action plan and invalidation triggers generated based on the proposed trade setup and confidence assessment.")

        # OUTPUT: Generate the Agent10_ActionPlan_Output JSON
        return Agent10_ActionPlan_Output(
            action_plan=action_plan_list,
            invalidation_triggers=invalidation_triggers_list,
            notes=notes
        )
