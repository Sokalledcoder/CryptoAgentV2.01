# This file makes the 'agents' directory a Python package.
# It also exposes agents for discovery and programmatic use.

# from .context_agent import root_agent as context_agent # Removed as context_agent.py now defines a class
from .orchestrator_agent import root_agent as orchestrator_agent
# Add other agents here as they are created
