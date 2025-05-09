import { useState, useEffect, useRef } from "react";
import "./index.css";
import { v4 as uuidv4 } from "uuid";

function App() {
  const [sessionId, setSessionId] = useState(() => localStorage.getItem("session_id") || uuidv4());
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

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

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

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
    setSidebarOpen(false);
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className={`flex h-screen ${darkMode ? 'bg-[#0f1117] text-gray-100' : 'bg-gray-50 text-gray-800'} transition-colors duration-200`}>
      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-10"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div 
        className={`fixed md:static inset-y-0 left-0 z-20 flex flex-col w-72 ${darkMode ? 'bg-[#1a1c25]' : 'bg-white'} 
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'} 
        transition-transform duration-300 ease-in-out shadow-lg md:shadow-none`}
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-700/20">
          <h1 className="text-xl font-bold">VerifastAI</h1>
          <button 
            onClick={toggleDarkMode}
            className={`p-2 rounded-full ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-200'}`}
          >
            {darkMode ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            )}
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <button
            onClick={resetSession}
            className={`flex items-center gap-2 w-full px-4 py-3 text-sm rounded-lg 
            ${darkMode ? 'bg-gray-700/40 hover:bg-gray-700/60' : 'bg-gray-200 hover:bg-gray-300'} 
            transition-colors duration-200`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            New Chat
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col relative">
        {/* Header (mobile only) */}
        <header className={`md:hidden ${darkMode ? 'bg-[#1a1c25]' : 'bg-white'} border-b ${darkMode ? 'border-gray-700/20' : 'border-gray-200'} p-4 flex justify-between items-center`}>
          <button onClick={toggleSidebar} className="p-1">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 className="text-lg font-semibold">VerifastAI</h1>
          <button onClick={resetSession} className="p-1">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
        </header>

        {/* Chat Area */}
        <div className={`flex-1 overflow-y-auto py-6 px-4 md:px-8 space-y-6 ${darkMode ? 'bg-[#0f1117]' : 'bg-gray-50'}`}>
          {messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="text-5xl mb-6 opacity-80">🤖</div>
              <h2 className={`text-2xl font-semibold mb-2 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                How can I help you today?
              </h2>
              <p className={`max-w-md ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                Ask me anything or start a conversation. I'm here to assist you.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`${msg.role === "bot" ? `${darkMode ? 'bg-[#1a1c25]' : 'bg-white'}` : 'bg-transparent'} 
              ${msg.role === "bot" ? 'py-6 px-4 md:px-8 -mx-4 md:-mx-8' : 'py-3 px-4'} 
              transition-colors duration-200`}
            >
              <div className="max-w-3xl mx-auto flex items-start gap-4">
                {msg.role === "bot" ? (
                  <div className="w-8 h-8 flex-shrink-0 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium">
                    A
                  </div>
                ) : (
                  <div className="w-8 h-8 flex-shrink-0 rounded-full bg-gray-500 flex items-center justify-center text-white font-medium">
                    U
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <div className={`${msg.role === "bot" ? (darkMode ? 'text-gray-200' : 'text-gray-800') : (darkMode ? 'text-gray-300' : 'text-gray-700')} whitespace-pre-wrap text-sm md:text-base leading-relaxed`}>
                    {msg.text}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className={`${darkMode ? 'bg-[#1a1c25]' : 'bg-white'} py-6 px-4 md:px-8 -mx-4 md:-mx-8`}>
              <div className="max-w-3xl mx-auto flex items-start gap-4">
                <div className="w-8 h-8 flex-shrink-0 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium">
                  A
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse" style={{ animationDelay: "0ms" }}></div>
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse" style={{ animationDelay: "300ms" }}></div>
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse" style={{ animationDelay: "600ms" }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className={`w-full ${darkMode ? 'bg-[#1a1c25]' : 'bg-white'} border-t ${darkMode ? 'border-gray-700/20' : 'border-gray-200'} p-4`}>
          <div className="max-w-3xl mx-auto">
            <div className={`relative rounded-lg border ${darkMode ? 'bg-[#2a2d3a] border-gray-700/50' : 'bg-white border-gray-300'} shadow-sm focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 transition-all duration-200`}>
              <textarea
                ref={textareaRef}
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
                className={`w-full resize-none px-4 py-3 pr-12 text-sm md:text-base focus:outline-none ${darkMode ? 'bg-[#2a2d3a] text-white placeholder-gray-500' : 'bg-white text-gray-800 placeholder-gray-400'} rounded-lg max-h-40`}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className={`absolute right-2 bottom-2 p-2 rounded-lg ${input.trim() ? 'bg-blue-600 hover:bg-blue-700' : darkMode ? 'bg-gray-700 text-gray-400' : 'bg-gray-200 text-gray-400'} transition-colors duration-200`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
              </button>
            </div>
            <div className="text-xs text-center mt-2 text-gray-500">
              Press Enter to send, Shift+Enter for new line
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;