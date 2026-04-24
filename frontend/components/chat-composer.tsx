"use client";

import { FormEvent, useState } from "react";
import { SendHorizontal } from "lucide-react";

type ChatComposerProps = {
  onSend: (message: string) => Promise<void>;
  loading: boolean;
};

export function ChatComposer({ onSend, loading }: ChatComposerProps) {
  const [message, setMessage] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = message.trim();

    if (!trimmed) {
      setValidationError("Please enter symptoms before sending.");
      return;
    }

    if (trimmed.length < 12) {
      setValidationError("Please provide a bit more detail, such as duration, severity, or other symptoms.");
      return;
    }

    setValidationError(null);
    setMessage("");
    await onSend(trimmed);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <label className="block">
        <span className="sr-only">Describe your symptoms</span>
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          rows={4}
          placeholder="Example: I have fever, body pain, sore throat, and fatigue for the past two days."
          className="w-full rounded-[1.5rem] border border-surface-700 bg-surface-800 px-4 py-3 text-sm text-ink shadow-sm outline-none transition placeholder:text-ink-muted focus:border-primary focus:ring-2 focus:ring-primary/20"
          disabled={loading}
        />
      </label>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs leading-6 text-ink-muted">
          Do not use this app for emergencies. Seek urgent care for chest pain, trouble breathing,
          seizures, stroke symptoms, severe bleeding, or self-harm risk.
        </p>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-primaryHover disabled:cursor-not-allowed disabled:opacity-60"
        >
          <SendHorizontal className="h-4 w-4" />
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
      {validationError ? (
        <p className="rounded-2xl bg-amber-900/30 px-4 py-3 text-sm text-amber-500">{validationError}</p>
      ) : null}
    </form>
  );
}
