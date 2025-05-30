# System Patterns: Crypto TA Multi-Agent System

**Version:** 0.2
**Date:** 2025-05-29

## 1. Overall Architecture

*   **Multi-Agent System (MAS):** The core of the system will be a collection of specialized AI agents.
*   **Orchestration:** A primary "Orchestrator Agent" will manage the overall workflow, delegate tasks to specialized agents, and aggregate results.
*   **Layered Communication:**
    *   **Agent-to-Agent:** Google A2A Protocol. (Initially, programmatic ADK calls within Orchestrator; A2A for future decoupling).
    *   **Agent-to-Frontend (User):** AG-UI Protocol over Server-Sent Events (SSE).
*   **Backend Services:** Python backend built with FastAPI to serve the AG-UI events and host the Orchestrator Agent.
*   **Frontend Application:** Single Page Application (SPA) built with React and CopilotKit.

## 2. Key Technical Decisions

*   **Agent Framework:** Google Agent Development Kit (ADK) for Python will be used to build all agents. This provides flexibility and tools for agent creation, including LLM integration (Gemini) and custom tool definition.
*   **Modularity:** Each of the 12 TA steps (derived from user prompts) will be implemented as a distinct, specialized ADK agent. This promotes separation of concerns and easier maintenance/upgrades.
*   **Data Flow:** JSON will be the primary data exchange format between agents (via A2A) and for the final output. Pydantic will be used for data validation within agents.
*   **External Data Integration:** MCP servers will be accessed via dedicated tool functions within the relevant ADK agents.
*   **Knowledge Retrieval:** A RAG (Retrieval Augmented Generation) system will be integrated to provide agents with contextual information from a managed knowledge base.

## 3. Component Relationships (Initial High-Level)

*   **User -> React/CopilotKit Frontend:** Initiates analysis, views results.
*   **React/CopilotKit Frontend <-> AG-UI (via SSE) <-> FastAPI Backend:** Handles user interaction events.
*   **FastAPI Backend -> Orchestrator ADK Agent (programmatic invocation):** Triggers and manages the main analysis workflow.
*   **Orchestrator ADK Agent -> Programmatic ADK Calls / (Future: A2A Protocol) -> Specialized ADK Task Agents:** Orchestrator delegates tasks and receives results from specialized agents.
*   **Specialized ADK Agents -> MCP Server Tool Functions:** Agents call internal Python functions that make HTTP requests to the respective MCP servers.
*   **Specialized ADK Agents -> RAG System Tool Function:** Agents query the RAG system for relevant knowledge.

## 4. Critical Implementation Paths

*   Establishing robust A2A communication between ADK agents.
*   Correctly implementing the AG-UI event emission from the FastAPI backend and consumption by CopilotKit.
*   Ensuring seamless data transformation and validation between agent outputs and inputs.
*   Programmatic invocation and data passing between the Orchestrator ADK Agent and Specialized ADK Task Agents.
*   Correctly structuring ADK agents within the project for discovery by `adk web` (for individual testing) and for programmatic invocation.

## 5. Operational Rules

*   **Command Execution Verification:** NEVER ASSUME COMMANDS RUN SUCCESSFULLY IF FULL TERMINAL OUTPUT IS NOT AVAILABLE OR CLEARLY INDICATES SUCCESS. ALWAYS RERUN COMMANDS OR ASK FOR USER ASSISTANCE/CONFIRMATION IF OUTPUT IS AMBIGUOUS OR MISSING.
*   **Package Installation Verification:** Before suggesting `pip install` (or similar package installation commands), cross-reference the package name and recommended version using available tools (e.g., Perplexity search for official documentation, PyPI, or GitHub repository) to ensure accuracy.
*   **Python Import Paths (Namespace Packages):** Crucially verify the correct import path for installed packages, especially for namespace packages (e.g., `google.adk` is imported from the `google` namespace, not as a top-level `google_adk`). Misunderstanding this can lead to persistent `ModuleNotFoundError` even if `pip list` shows the package. The module files will reside within the namespace directory in `site-packages` (e.g., `venv/Lib/site-packages/google/adk/`).
