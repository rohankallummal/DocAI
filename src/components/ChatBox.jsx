import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      setTimeout(() => chatEndRef.current.scrollIntoView({ behavior: "smooth" }), 100);
    }
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    const formData = new FormData();
    formData.append("question", input);
    formData.append("top_k", topK);

    try {
      const res = await axios.post("http://localhost:8000/query", formData);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: res.data.answer || "No response received.",
        },
      ]);
    } catch (err) {
      const msg = err.response?.data?.message || "Server error!";
      setMessages((prev) => [...prev, { sender: "bot", text: msg }]);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      await axios.post("http://localhost:8000/reset");
    } catch (err) {
      console.warn(" Backend reset unavailable");
    }
    localStorage.removeItem("uploaded");
    setTimeout(() => {
      window.location.reload();
    }, 100);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <ion-icon name="chatbubbles-outline" style={{ fontSize: "1.4em" }}></ion-icon>
          <span>DocAI</span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <label htmlFor="topk" style={{ fontSize: "0.9em", color: "#aaa" }}>
            Chunks:
          </label>
          <select
            id="topk"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="topk-selector"
          >
            {[3, 5, 7, 10, 15].map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>

          <button className="reset-button" onClick={handleReset} title="Reset chat">
            <ion-icon name="exit-outline"></ion-icon>
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`chat-row ${msg.sender === "user" ? "user-row" : "bot-row"}`}
          >
            {msg.sender === "bot" ? (
              <>
                <ion-icon
                  name="hardware-chip-outline"
                  className="chat-icon bot-icon"
                ></ion-icon>
                <div className="chat-bubble assistant-bubble">{msg.text}</div>
              </>
            ) : (
              <>
                <div className="chat-bubble user-bubble">{msg.text}</div>
                <ion-icon
                  name="person-outline"
                  className="chat-icon user-icon"
                ></ion-icon>
              </>
            )}
          </div>
        ))}

        {loading && <div className="typing-indicator">Thinking</div>}
        <div ref={chatEndRef} />
      </div>

      <form className="chat-input-area" onSubmit={sendMessage}>
        <div className="input-wrapper">
          <ion-icon name="pencil-outline" className="input-icon"></ion-icon>
          <input
            type="text"
            placeholder="Ask Doc"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            autoFocus
          />
        </div>
        <button type="submit" disabled={loading} title="Send">
          <ion-icon name="arrow-up-circle-outline"></ion-icon>
        </button>
      </form>
    </div>
  );
}
