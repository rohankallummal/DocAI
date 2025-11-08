import React, { useState, useEffect } from "react";
import FileUploader from "./components/FileUploader";
import ChatBox from "./components/ChatBox";
import "./App.css";

export default function App() {
  const [uploaded, setUploaded] = useState(false);

  useEffect(() => {
    const wasUploaded = localStorage.getItem("uploaded") === "true";
    if (wasUploaded) setUploaded(true);
  }, []);

  const handleUploadComplete = () => {
    localStorage.setItem("uploaded", "true");
    setUploaded(true);
  };

  return (
    <div className="app-container">
      {!uploaded ? (
        <FileUploader onUploadComplete={handleUploadComplete} />
      ) : (
        <ChatBox />
      )}
    </div>
  );
}
