"use client";

import { useEffect, useRef } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export function ChatWindow({
  messages,
  input,
  onInputChange,
  onSubmit,
  isLoading
}: {
  messages: Message[];
  input: string;
  onInputChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
}) {
  const chatLogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatLogRef.current) {
      chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Conversation</h2>
        <p>Send a message and inspect how each memory system reacts.</p>
      </div>
      <div className="chat-log" ref={chatLogRef}>
        {messages.length === 0 ? <p className="empty">No messages yet.</p> : null}
        {messages.map((message, index) => (
          <article key={`${message.role}-${index}`} className={`bubble ${message.role}`}>
            <strong>{message.role === "user" ? "User" : "Assistant"}</strong>
            <p>{message.content}</p>
          </article>
        ))}
      </div>
      <div className="composer">
        <textarea
          value={input}
          onChange={(event) => onInputChange(event.target.value)}
          placeholder="Tell the assistant something important to remember."
        />
        <button onClick={onSubmit} disabled={isLoading || !input.trim()}>
          {isLoading ? "Sending..." : "Send"}
        </button>
      </div>
    </section>
  );
}

