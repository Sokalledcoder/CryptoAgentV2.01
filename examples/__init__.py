# This file makes the 'examples' directory a Python package.
# The root_agent is defined directly here for ADK web discovery.
from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    model="gemini-2.5-flash-preview-05-20", 
    name="hello_agent", 
    description="A simple agent that says hello.",
    instruction="You are a friendly agent. When the user says 'ping', you reply with 'pong'."
)
