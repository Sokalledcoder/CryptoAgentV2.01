import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <CopilotKit runtimeUrl="http://localhost:3000/api/copilotkit">
      <App />
    </CopilotKit>
  </StrictMode>,
)
