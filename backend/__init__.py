# This file makes the 'backend' directory a Python package.
# It exposes the OrchestratorAgent as the root_agent for ADK web discovery.

# Ensure .env is loaded if ADK tries to load this package directly
from dotenv import load_dotenv
import os
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    print(f"Warning: .env file not found at {dotenv_path} when initializing backend package.")

# Import and expose OrchestratorAgent as the root_agent for the 'backend' package
try:
    # The orchestrator_agent is imported from backend.agents (which is backend/agents/__init__.py)
    # and that __init__.py imports the actual root_agent from orchestrator_agent.py
    from .agents import orchestrator_agent
    root_agent = orchestrator_agent 
    print(f"Backend package initialized. Root agent set to: OrchestratorAgent (name: {root_agent.name if root_agent else 'None'})")
except ImportError as e:
    print(f"Error importing orchestrator_agent from .agents for backend root: {e}")
    root_agent = None # Fallback if import fails
except AttributeError as e:
    print(f"AttributeError: orchestrator_agent might not be exposed correctly in .agents: {e}")
    root_agent = None


if root_agent is None:
    print("CRITICAL: root_agent for backend package could not be set.")
