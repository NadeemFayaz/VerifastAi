"use client"

import { useState, useEffect } from "react"
import { User, Bot } from "lucide-react"

// Removed TypeScript interfaces and type annotations

export function ChatMessage({ message }) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    // Add a small delay before showing the message for a nice animation effect
    const timer = setTimeout(() => {
      setVisible(true)
    }, 100)

    return () => clearTimeout(timer)
  }, [])

  const isUser = message.role === "user"

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} transition-opacity duration-300 ease-in-out ${visible ? "opacity-100" : "opacity-0"}`}
    >
      <div className={`flex max-w-[80%] ${isUser ? "flex-row-reverse" : "flex-row"} items-start gap-2`}>
        <div
          className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${isUser ? "bg-slate-700" : "bg-emerald-600"}`}
        >
          {isUser ? <User className="h-4 w-4 text-white" /> : <Bot className="h-4 w-4 text-white" />}
        </div>

        <div
          className={`py-2 px-3 rounded-lg ${
            isUser
              ? "bg-slate-700 text-white rounded-tr-none"
              : "bg-white border border-slate-200 shadow-sm rounded-tl-none"
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{message.text}</p>
        </div>
      </div>
    </div>
  )
}