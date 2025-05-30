# Product Context: Crypto TA Multi-Agent System

**Version:** 0.2
**Date:** 2025-05-29

## 1. Why This Project?

The project aims to revolutionize the process of cryptocurrency technical analysis by leveraging advanced AI agent technologies. It addresses the need for a more automated, consistent, in-depth, and efficient way to analyze market charts and data, moving beyond manual or simplistic tools.

## 2. Problems It Solves

*   **Time-Consuming Manual Analysis:** Automates a complex, multi-step TA workflow that is currently performed manually.
*   **Consistency:** Ensures a standardized analytical process across different analyses.
*   **Depth of Analysis:** Allows for deep, specialized analysis by dedicating individual agents to specific tasks (e.g., market structure, liquidity, sentiment).
*   **Information Overload:** Helps synthesize vast amounts of data (chart visuals, MCP data, RAG knowledge) into actionable insights.
*   **Real-time Interaction:** Provides a modern, interactive front-end for users to engage with the analysis process.

## 3. How It Should Work (User Experience Goals)

*   **Initiation:** The user should be able to easily initiate an analysis by providing a chart image and relevant parameters (e.g., symbol, timeframe) through a web interface.
*   **Real-time Feedback:** The front-end should provide real-time updates on the agent's progress, streaming messages, tool call information, and intermediate findings as they become available (via AG-UI).
*   **Displaying Progress:** Displaying progress through the 12-step analysis as the Orchestrator agent receives results from specialized task agents.
*   **Clarity of Results:** The final output should be a clear, structured JSON report, supplemented by a human-readable summary. Intermediate steps should also be accessible.
*   **Interactivity (Future):** Potentially allow for human-in-the-loop interactions where the user can guide or provide input at certain stages.
*   **Reliability:** The system should be robust and handle errors gracefully.

## 4. Target User

Primarily the project owner (a sophisticated crypto trader/analyst) who requires a powerful, customized tool to augment their analytical capabilities.
