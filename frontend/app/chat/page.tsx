"use client";

import Link from "next/link";
import { useState, useRef, useEffect } from "react";
import { ArrowLeft, Stethoscope } from "lucide-react";

import { chat } from "@/lib/api";
import type { ChatResponse } from "@/types/api";
import { AssistantResponseCard } from "@/components/assistant-response-card";
import { ChatComposer } from "@/components/chat-composer";

type Message =
  | { id: string; role: "user"; content: string }
  | { id: string; role: "assistant"; content: string; payload?: ChatResponse };

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello! I am MedAssist AI. Share your symptoms, how long you've had them, and their severity. I will retrieve relevant medical knowledge to help guide you.",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (message: string) => {
    setError(null);
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
    };
    setMessages((current) => [...current, userMessage]);
    setLoading(true);

    try {
      const response = await chat(message);
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.response,
        payload: response,
      };
      setMessages((current) => [...current, assistantMessage]);
    } catch (caught) {
      const message =
        caught instanceof Error
          ? caught.message
          : "Something went wrong while contacting the backend.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex h-screen flex-col bg-surface-900">
      <header className="flex-none border-b border-surface-800 bg-surface-900/80 p-4 backdrop-blur sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-4xl items-center justify-between">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm font-medium text-ink-muted transition hover:text-primary"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to home
          </Link>
          <div className="text-sm font-semibold text-ink">MedAssist AI</div>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col overflow-y-auto px-4 pb-48 pt-8 sm:px-6">
        <div className="space-y-8">
          {messages.map((message) => (
            <div
              key={message.id}
              className={message.role === "user" ? "ml-auto max-w-2xl" : "mr-auto w-full"}
            >
              {message.role === "user" ? (
                <div className="rounded-3xl bg-surface-800 px-5 py-4 text-[0.95rem] leading-7 text-ink">
                  {message.content}
                </div>
              ) : (
                <div className="flex gap-4">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/20 text-primary">
                    <Stethoscope className="h-4 w-4" />
                  </div>
                  <div className="mt-1 flex-1 space-y-2">
                    {message.payload ? (
                      <AssistantResponseCard response={message.payload} />
                    ) : (
                      <p className="text-[0.95rem] leading-7 text-ink">{message.content}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="mr-auto flex gap-4 w-full">
               <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/20 text-primary">
                  <Stethoscope className="h-4 w-4" />
               </div>
               <div className="mt-1 flex items-center h-8">
                  <div className="flex space-x-2">
                    <div className="h-2 w-2 animate-bounce rounded-full bg-primary/60"></div>
                    <div className="h-2 w-2 animate-bounce rounded-full bg-primary/60" style={{ animationDelay: '0.2s' }}></div>
                    <div className="h-2 w-2 animate-bounce rounded-full bg-primary/60" style={{ animationDelay: '0.4s' }}></div>
                  </div>
               </div>
            </div>
          )}
          
          <div ref={endOfMessagesRef} />
        </div>
      </div>

      <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-surface-900 via-surface-900 to-transparent pb-6 pt-16">
        <div className="mx-auto max-w-3xl px-4 sm:px-6">
          <ChatComposer onSend={handleSend} loading={loading} />
          {error ? (
            <p className="mt-3 rounded-2xl bg-red-900/40 px-4 py-3 text-sm text-red-400">
              {error}
            </p>
          ) : null}
          <p className="mt-3 text-center text-xs tracking-tight text-ink-muted">
            MedAssist AI is an educational tool. Always verify output with a licensed healthcare professional.
          </p>
        </div>
      </div>
    </main>
  );
}
