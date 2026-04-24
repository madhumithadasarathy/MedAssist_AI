"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowLeft } from "lucide-react";

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
        "Share your symptoms, how long they have been happening, and how severe they feel. I’ll return educational guidance, not a medical diagnosis.",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
        content: response.assistant_response,
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
    <main className="min-h-screen bg-gradient-to-b from-mist via-white to-white px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        <div className="flex items-center justify-between">
          <div>
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-sm font-medium text-slateblue/75 transition hover:text-teal"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to home
            </Link>
            <h1 className="mt-3 text-3xl font-semibold text-slateblue">MedAssist AI Chat</h1>
            <p className="mt-2 max-w-2xl text-sm leading-7 text-slateblue/75">
              Describe symptoms in natural language. Emergency red flags will trigger an urgent
              care warning. This tool does not replace a clinician.
            </p>
          </div>
        </div>

        <section className="rounded-[2rem] border border-slateblue/10 bg-white p-4 shadow-panel sm:p-6">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={
                  message.role === "user"
                    ? "ml-auto max-w-2xl rounded-[1.5rem] bg-slateblue px-4 py-3 text-sm leading-7 text-white"
                    : "mr-auto max-w-3xl"
                }
              >
                {message.role === "assistant" && message.payload ? (
                  <AssistantResponseCard response={message.payload} />
                ) : (
                  <p>{message.content}</p>
                )}
              </div>
            ))}

            {loading ? (
              <div className="max-w-xl rounded-[1.5rem] border border-teal/10 bg-mist px-4 py-3 text-sm text-slateblue/70">
                Analyzing symptom patterns and retrieving related medical knowledge...
              </div>
            ) : null}
          </div>

          <div className="mt-6 border-t border-slateblue/10 pt-4">
            <ChatComposer onSend={handleSend} loading={loading} />
            {error ? (
              <p className="mt-3 rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>
            ) : null}
          </div>
        </section>
      </div>
    </main>
  );
}
