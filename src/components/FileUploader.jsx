import React, { useState } from "react";
import axios from "axios";
import "../App.css";

export default function FileUploader({ onUploadComplete }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError("");
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a PDF file to upload.");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post("http://localhost:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setTimeout(() => {
        setUploading(false);
        onUploadComplete(true);
      }, 2000);
    } catch (err) {
      console.error(err);
      setError("Upload failed. Please try again.");
      setUploading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="uploader">
        <div className="uploader-box">
          <h1>Upload Your PDF</h1>
          <p>Start chatting with DocAI</p>

          <form onSubmit={handleSubmit}>
            <div className="file-input-wrapper">
              {!file ? (
                <label className="file-label">
                  <ion-icon
                    name="cloud-upload-outline"
                    style={{
                      fontSize: "1.4em",
                      marginRight: "6px",
                      verticalAlign: "middle",
                    }}
                  ></ion-icon>
                  Choose File
                  <input
                    type="file"
                    accept="application/pdf"
                    onChange={handleFileChange}
                    style={{ display: "none" }}
                  />
                </label>
              ) : (
                <div className="file-chosen">
                  <span className="file-name">{file.name}</span>
                  <button
                    type="button"
                    className="remove-file-btn"
                    onClick={handleRemoveFile}
                    title="Remove file"
                  >
                    <ion-icon name="backspace-outline"></ion-icon>
                  </button>
                </div>
              )}
            </div>

            <button type="submit" disabled={uploading}>
              {uploading ? "Processing ..." : "Upload & Start"}
            </button>

            {error && <div className="error-message">{error}</div>}
          </form>
        </div>
      </div>
    </div>
  );
}
