"use client";

import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<{ user: string; bot: string }[]>([]);
  const [queryLoading, setQueryLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);

  const handleAsk = async () => {
    if (!question.trim() || queryLoading || uploadLoading) return;
    setQueryLoading(true);
    const userMsg = question;
    setQuestion("");

    try {
      const res = await axios.post(`${process.env.NEXT_PUBLIC_API_BASE_URL}/query`, {
        question: userMsg,
      });

      const botReply = res.data.answer;
      setMessages((prev) => [...prev, { user: userMsg, bot: botReply }]);
    } catch (error: any) {
      setMessages((prev) => [...prev, { user: userMsg, bot: "❌ Error fetching response." }]);
    } finally {
      setQueryLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadLoading(true);
    setMessages([]); // Clear previous messages on new file upload

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${process.env.NEXT_PUBLIC_API_BASE_URL}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      alert("✅ Upload successful: " + res.data.detail);
    } catch (err: any) {
      alert("❌ Upload failed: " + err?.response?.data?.detail || err.message);
    } finally {
      e.target.value = ""; // Reset the file input to allow re-uploading the same file
      setUploadLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 800, margin: "0 auto", padding: 20 }}>
      <h1>🧠 AI Tabular Analyst</h1>

      <input
        type="file"
        accept=".csv,.xlsx"
        onChange={handleFileUpload}
        disabled={uploadLoading || queryLoading}
        style={{ margin: "20px 0", display: "block" }}
      />
      {uploadLoading && <p>Uploading and processing file...</p>}

      <div>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: 12 }}>
            <p><strong>You:</strong> {msg.user}</p>
            <p><strong>Bot:</strong> {msg.bot}</p>
          </div>
        ))}
      </div>

      <textarea
        rows={3}
        placeholder="Ask a question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        disabled={queryLoading || uploadLoading}
        style={{ width: "100%", padding: 10, marginTop: 20 }}
      />

      <button
        onClick={handleAsk}
        disabled={queryLoading || uploadLoading}
        style={{ marginTop: 10, padding: "10px 20px" }}
      >
        {queryLoading ? "Thinking..." : "Ask"}
      </button>
    </main>
  );
}