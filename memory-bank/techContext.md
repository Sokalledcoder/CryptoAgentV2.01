# Technology Context: Crypto TA Multi-Agent System

**Version:** 0.2
**Date:** 2025-05-29

## 1. Core Technologies

*   **Backend Language:** Python (version 3.9+)
*   **Agent Development:** Google Agent Development Kit (ADK) for Python
*   **Inter-Agent Communication:** Google A2A Protocol (Python SDK: `a2a-sdk`)
*   **Agent-User Interaction:** AG-UI Protocol (Python SDK: `ag-ui-protocol`)
*   **Web Framework (Backend):** FastAPI (for serving AG-UI SSE endpoint and A2A endpoints)
*   **Real-time Transport:** Server-Sent Events (SSE)
*   **Frontend Framework:** React (with Vite or Create React App)
*   **Frontend Agent Integration:** CopilotKit
*   **Primary LLM:** Google Gemini (accessed via Google ADK, using Google AI Studio API Key via `.env` for local development: `GOOGLE_GENAI_USE_VERTEXAI=FALSE`)
*   **External Data Sources:**
    *   CoinGecko MCP Server
    *   Fear & Greed MCP Server
    *   Perplexity MCP Server
*   **Data Validation:** Pydantic
*   **HTTP Client (for MCP calls):** `requests` library

## 2. Development Environment

*   **Version Control:** Git
*   **Package Management:**
    *   Python: `pip` with `requirements.txt` (managed within a virtual environment like `venv`).
    *   JavaScript/TypeScript: `npm` or `yarn`.
*   **IDE:** Visual Studio Code (recommended by user)
*   **Operating System (User):** Windows 10 (important for pathing, shell commands if any)

## 3. Knowledge Retrieval (RAG System - Planned)

*   **Vector Storage:** To be determined (options: existing OpenAI vector store if accessible, Google Vertex AI Search, self-hosted ChromaDB/FAISS).
*   **Embedding Models:** To be determined (options: OpenAI embeddings, Sentence Transformers, Google embedding models).
*   **Document Types:** Markdown files primarily.

## 4. Deployment (Future Consideration)

*   **Backend:** Containerization (Docker), potential deployment on Google Cloud Run, Kubernetes, or dedicated server.
*   **Frontend:** Vercel, Netlify, Google Cloud App Engine, or similar static/Node.js hosting.

## 5. Key Libraries & SDKs to Install

*   `google-adk`
*   `a2a-sdk`
*   `ag-ui-protocol`
*   `fastapi`
*   `uvicorn` (ASGI server for FastAPI)
*   `python-dotenv`
*   `requests`
*   `pydantic`
*   (For RAG, later): `langchain`, `llama-index`, specific vector DB clients, sentence-transformers, etc.
*   (Frontend): `react`, `react-dom`, `@copilotkit/react-core`, `@copilotkit/react-ui`, `@copilotkit/react-textarea`
