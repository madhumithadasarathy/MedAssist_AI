"use client";

import { FormEvent, useState, useRef, useEffect } from "react";
import { ArrowUp } from "lucide-react";

type ChatComposerProps = {
  onSend: (message: string) => Promise<void>;
  loading: boolean;
};

export function ChatComposer({ onSend, loading }: ChatComposerProps) {
  const [message, setMessage] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [message]);

  const handleSubmit = async (event: FormEvent | React.KeyboardEvent) => {
    event.preventDefault();
    const trimmed = message.trim();

    if (!trimmed) {
      return;
    }

    if (trimmed.length < 12) {
      setValidationError("Please provide a bit more detail (duration, severity, etc).");
      return;
    }

    setValidationError(null);
    setMessage("");
    await onSend(trimmed);
  };

  return (
    <form onSubmit={handleSubmit} className="relative flex w-full flex-col items-center">
      <div className="relative flex w-full max-w-3xl items-end rounded-[1.5rem] bg-surface-800 shadow-panel transition-all focus-within:ring-2 focus-within:ring-primary/20">
        <label className="flex w-full cursor-text">
          <span className="sr-only">Describe your symptoms</span>
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            rows={1}
            placeholder="Message MedAssist AI..."
            className="w-full resize-none border-none bg-transparent px-5 py-4 text-[0.95rem] text-ink outline-none placeholder:text-ink-muted"
            style={{ minHeight: '56px', maxHeight: '200px' }}
            disabled={loading}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
        </label>
        <div className="pointer-events-none absolute bottom-2 right-2 flex h-10 w-10 items-center justify-center">
          <button
            type="submit"
            disabled={loading || !message.trim()}
            className="pointer-events-auto flex h-8 w-8 items-center justify-center rounded-full bg-ink text-surface-900 transition hover:bg-ink-muted disabled:cursor-not-allowed disabled:opacity-20"
          >
            <ArrowUp className="h-4 w-4 shrink-0" strokeWidth={3} />
          </button>
        </div>
      </div>
      {validationError ? (
        <p className="absolute -top-10 rounded-full bg-amber-900/40 px-4 py-2 text-xs font-medium text-amber-500">
          {validationError}
        </p>
      ) : null}
    </form>
  );
}
