import asyncio
import os
from dotenv import load_dotenv

# Ensure .env is loaded from the project root
# This script is in backend/, so project root is one level up.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print(f"Loaded .env file from: {dotenv_path}")
else:
    print(f"Warning: .env file not found at {dotenv_path}")

# Import the orchestrator_agent instance
# This comes from backend/agents/__init__.py, which imports it from backend/agents/orchestrator_agent.py
try:
    from backend.agents import orchestrator_agent
    print(f"Successfully imported orchestrator_agent: {orchestrator_agent.name}")
except ImportError as e:
    print(f"Failed to import orchestrator_agent: {e}")
    orchestrator_agent = None
except AttributeError as e:
    print(f"Failed to access orchestrator_agent, possibly not exposed correctly: {e}")
    orchestrator_agent = None


async def main():
    if not orchestrator_agent:
        print("Orchestrator agent not available. Exiting.")
        return

    test_query = "Analyze BTCUSDT 4H chart from Bybit for current context."
    print(f"\nSending query to orchestrator_agent: '{test_query}'")

    try:
        # How to invoke an LlmAgent directly?
        # Option 1: If the agent itself is awaitable (common in some frameworks)
        # response = await orchestrator_agent(test_query) # This is a guess

        # Option 2: Look for an invoke or process method (common in Langchain, etc.)
        # response = await orchestrator_agent.ainvoke({"input": test_query}) # Another guess
        # response = await orchestrator_agent.arun(test_query)

        # Option 3: The ADK LlmAgent might have a specific method.
        # The Runner uses `agent.process_event_async(event, invocation_context)`.
        # This is too low-level for a simple direct call.

        # Let's assume for now that the LlmAgent might be directly callable with a simple string
        # if its tools and instructions are set up for it.
        # The `Runner` eventually calls something like `self.agent.process_event_async`.
        # For a single-turn, non-streaming, direct invocation, the API might be simpler.
        # The Perplexity output said "This agent can be invoked ... as a Python object"
        # and "LlmAgent can process direct input programmatically".

        # The `google.adk.agents.Agent` base class (which LlmAgent inherits from)
        # has an `async def invoke(self, request: Any) -> AgentResponseEvent:` method.
        # This seems like the most promising candidate for direct invocation.
        # The `request` type is `Any`, so a string should be acceptable.
        
        print("Attempting to call orchestrator_agent.run()...")
        # Try the synchronous run method. ADK might handle async tools internally.
        # The parameter name 'request' is a guess. Perplexity showed 'input_text'.
        # If this is a synchronous method, we don't await it directly in this async main,
        # but for now, let's see if the method call itself works.
        # A proper way to call sync code from async is loop.run_in_executor.
        # For now, direct call to see if it resolves or gives a different error.
        # LlmAgent.run() is likely synchronous and returns the final response directly, not an event.
        response_output = orchestrator_agent.run(request=test_query) # No await
        
        print("\n--- Orchestrator Response Output ---")
        print(response_output) # This should be the direct output, likely a string or dict

        # Assuming response_output is the string that might contain JSON
        final_output_str = response_output 
        if isinstance(response_output, dict) and "output" in response_output: # Or however ADK structures it
            final_output_str = response_output["output"] 
        elif hasattr(response_output, 'text'): # If it's some kind of response object
             final_output_str = response_output.text


        if final_output_str and isinstance(final_output_str, str):
            print("\n--- Extracted Output String ---")
            print(final_output_str)
            try:
                import json
                parsed_json = json.loads(final_output_str)
                print("\n--- Parsed JSON Output ---")
                import pprint
                pprint.pprint(parsed_json)
            except json.JSONDecodeError:
                print("\n--- Output string is not valid JSON ---")
        elif final_output_str: # If it was already a dict/object
             print("\n--- Output (already structured) ---")
             import pprint
             pprint.pprint(final_output_str)
        else:
            print("\n--- No valid output from agent ---")

    except Exception as e:
        print(f"\nError during direct agent invocation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if orchestrator_agent:
        asyncio.run(main())
    else:
        print("Skipping asyncio.run(main()) because orchestrator_agent failed to import.")
