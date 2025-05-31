import React, { useState } from "react";
import type { ChangeEvent } from "react";
import "./App.css";
import { CopilotChat } from "@copilotkit/react-ui";

// The Python FastAPI backend (with the actual action and image upload) is at http://localhost:8000
const pythonFastAPIEndpoint = "http://localhost:8000";

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setUploadedImageUrl(null); // Reset previous URL if a new file is selected
      setUploadError(null);
    } else {
      setSelectedFile(null);
    }
  };

  const handleImageUpload = async () => {
    if (!selectedFile) {
      setUploadError("Please select a file first.");
      return;
    }

    setUploading(true);
    setUploadError(null);
    setUploadedImageUrl(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(`${pythonFastAPIEndpoint}/upload-chart-image/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "Unknown error during upload." }));
        throw new Error(`Upload failed: ${response.statusText} - ${errorData.message || 'Server error'}`);
      }

      const result = await response.json();
      if (result.file_url) {
        setUploadedImageUrl(result.file_url);
        setSelectedFile(null); 
        // console.log("Image uploaded:", result.file_url);
      } else {
        throw new Error("Upload succeeded but no file_url received from backend.");
      }
    } catch (error: any) {
      console.error("Upload error:", error);
      setUploadError(error.message || "An unexpected error occurred during upload.");
    } finally {
      setUploading(false);
    }
  };

  // Dynamically construct system message for CopilotChat
  let dynamicInstructions = "You are a helpful AI assistant for cryptocurrency technical analysis. ";
  if (uploadedImageUrl) {
    dynamicInstructions += `An image has been uploaded for analysis: ${uploadedImageUrl}. If the user asks to analyze a chart or image, assume they mean this one unless they specify otherwise. When you decide to call the 'runCryptoTaOrchestrator' action for image analysis, ensure you include this URL in the 'image_url' parameter of that action.`;
  }


  return (
    // Assuming CopilotKit provider is in main.tsx, pointing to the Node.js runtime
    // e.g., <CopilotKit url="http://localhost:3000/api/copilotkit/"> wraps <App /> in main.tsx
    <div className="App">
      <header className="App-header">
        <h1>Crypto TA Copilot</h1>
        <div className="upload-section">
          <input type="file" accept="image/*" onChange={handleFileChange} />
          <button onClick={handleImageUpload} disabled={!selectedFile || uploading}>
            {uploading ? "Uploading..." : "Upload Chart Image"}
          </button>
          {uploadError && <p className="error-message">Error: {uploadError}</p>}
          {uploadedImageUrl && (
            <div className="success-message">
              <p>Image ready for analysis: <a href={uploadedImageUrl} target="_blank" rel="noopener noreferrer" title={uploadedImageUrl}>Link to Image</a></p>
              <p>Now you can ask the Copilot to analyze it, e.g., "Analyze this chart for BTCUSDT 1H".</p>
            </div>
          )}
        </div>
      </header>
      <div className="chat-container">
        <CopilotChat
          instructions={dynamicInstructions}
          // The 'runCryptoTaOrchestrator' action is defined on the Python backend.
          // The Node.js runtime (configured via CopilotKit provider's `url` prop in main.tsx)
          // needs to be set up to proxy calls to this action to the Python backend.
        />
      </div>
    </div>
  );
}

export default App;
