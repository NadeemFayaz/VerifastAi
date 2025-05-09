import { useState, useEffect, useRef } from "react";
import "./index.css";
import { v4 as uuidv4 } from "uuid";

function App() {
  const [sessionId, setSessionId] = useState(() => localStorage.getItem("session_id") || uuidv4());
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    localStorage.setItem("session_id", sessionId);
    fetch(`http://localhost:8000/history/${sessionId}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setMessages(data);
        } else if (data && typeof data === 'object') {
          setMessages(data.messages || []);
        } else {
          console.error("Invalid data format:", data);
          setMessages([]);
        }
      })
      .catch(err => {
        console.error("Fetch error:", err);
        setMessages([]);
      });
  }, [sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setLoading(true);
    const userMessage = { role: "user", text: input };
    setMessages(prev => [...prev, userMessage]);

    try {
      const formData = new FormData();
      formData.append("query", input);
      formData.append("session_id", sessionId);

      const res = await fetch(`http://localhost:8000/chat`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      const botMessage = { role: "bot", text: data.answer };
      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: "bot", text: "Sorry, something went wrong." }]);
    }

    setInput("");
    setLoading(false);
  };

  const resetSession = async () => {
    await fetch(`http://localhost:8000/session/${sessionId}`, { method: "DELETE" });
    const newId = uuidv4();
    localStorage.setItem("session_id", newId);
    setSessionId(newId);
    setMessages([]);
  };

  return (
    <div className="flex h-screen bg-gray-100 text-gray-800">
      {/* Sidebar */}
      <div className="hidden md:flex flex-col w-64 bg-[#111827] text-white p-4 space-y-4 shadow-md">
        <h1 className="text-xl font-bold">VerifastAI</h1>
        <button
          onClick={resetSession}
          className="flex items-center gap-2 px-4 py-2 text-sm bg-gray-800 rounded hover:bg-gray-700 transition"
        >
          <span className="text-xl">＋</span> New Chat
        </button>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col relative">
        {/* Header (mobile only) */}
        <header className="md:hidden bg-white border-b p-4 flex justify-between items-center">
          <h1 className="text-lg font-semibold">VerifastAI</h1>
          <button onClick={resetSession} className="text-gray-600 hover:text-black">
            <span className="text-xl">＋</span>
          </button>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
          {messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
              <div className="text-4xl mb-4">🤖</div>
              <p className="text-lg font-light">How can I help you today?</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex max-w-2xl mx-auto items-start space-x-3 ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {msg.role === "bot" && (
                <div className="w-10 h-10 flex items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white font-bold">
                  A
                </div>
              )}
              <div
                className={`p-4 rounded-xl text-sm shadow ${
                  msg.role === "bot"
                    ? "bg-white text-gray-800"
                    : "bg-blue-500 text-white"
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.text}</div>
              </div>
              {msg.role === "user" && (
                <div className="w-10 h-10 flex items-center justify-center rounded-full bg-gray-300 text-gray-700 font-bold">
                  U
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex max-w-2xl mx-auto items-start space-x-3">
              <div className="w-10 h-10 flex items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white font-bold">
                A
              </div>
              <div className="p-4 bg-white rounded-xl text-sm shadow text-gray-600">
                <div className="dot-typing"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="w-full bg-white border-t p-4">
          <div className="max-w-3xl mx-auto flex items-center gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              rows="1"
              placeholder="Type your message..."
              className="flex-1 resize-none rounded-md border border-gray-300 px-4 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700 disabled:opacity-40"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12l-3-9 18 9-18 9 3-9zm0 0h7.5" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
