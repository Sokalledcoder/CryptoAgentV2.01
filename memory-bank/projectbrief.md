# Project Brief: Crypto Technical Analysis Multi-Agent System

**Version:** 0.2
**Date:** 2025-05-29

## 1. Project Goal

To develop a sophisticated, multi-agent system capable of performing comprehensive cryptocurrency technical analysis. The system will ingest chart images, leverage specialized AI agents for different analytical tasks, utilize external data via MCP servers, incorporate a RAG system for up-to-date knowledge, and present findings through an interactive front-end.

## 2. Core Problem Statement

Current methods for performing detailed, multi-step crypto TA are manual, time-consuming, and may lack consistency. This project aims to automate and enhance this process by building a robust, modular, and intelligent agent-based system.

## 3. Scope

*   **Backend:**
    *   Development of an Orchestrator Agent and 12 specialized Task Agents using Google Agent Development Kit (ADK) for Python.
    *   Inter-agent communication primarily via programmatic ADK calls, with Google A2A Protocol as a potential future refinement for decoupling.
    *   Interaction with existing MCP servers (CoinGecko, Fear & Greed, Perplexity).
    *   Integration of a RAG system for knowledge retrieval.
    *   Image input processing and workspace management.
*   **Agent-User Interaction:**
    *   AG-UI Protocol from a FastAPI backend (hosting the Orchestrator Agent) over Server-Sent Events (SSE).
*   **Frontend:**
    *   React application using CopilotKit.
    *   User interface for initiating analysis, uploading images, and viewing streamed results.
*   **Workflow:** Based on the user-provided 12-step crypto TA prompt structure, adapted for a multi-agent architecture.

## 4. Key Objectives

*   Successfully implement and test a basic ADK agent.
*   Develop the Orchestrator Agent.
*   Implement FastAPI backend with AG-UI/SSE streaming.
*   Build a basic React/CopilotKit front-end to test end-to-end flow.
*   Iteratively develop and integrate the 12 specialized ADK Task Agents with MCP tool calls.
*   Integrate a RAG system.
*   Ensure the system can process chart images and produce a structured JSON `FinalReport`.
