import { AlertTriangle, BookOpenText, Tag } from "lucide-react";

import type { ChatResponse } from "@/types/api";

export function AssistantResponseCard({ response }: { response: ChatResponse }) {
  return (
    <article className="space-y-6 rounded-[1.75rem] border border-surface-700 bg-surface-800 p-4 shadow-panel sm:p-6 text-ink">
      {response.emergency ? (
        <div className="rounded-3xl border border-red-500/30 bg-red-900/20 p-4 text-red-400">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
            <div>
              <h2 className="font-semibold">Emergency warning</h2>
              <p className="mt-1 text-sm leading-7">
                {response.safety_message || "Red-flag symptoms were detected. Seek immediate medical help."}
              </p>
            </div>
          </div>
        </div>
      ) : null}

      <section>
        <h2 className="text-lg font-semibold">Assistant response</h2>
        <p className="mt-2 whitespace-pre-line text-sm leading-7 text-ink-muted">
          {response.response}
        </p>
      </section>

      {response.why && response.why.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-3">
            <Tag className="h-4 w-4 text-primary" />
            <h2 className="text-sm font-semibold uppercase tracking-wider">Key Indicators</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {response.why.map((term) => (
              <span key={term} className="rounded-full bg-surface-700 px-3 py-1 text-xs font-medium text-primary border border-primary/20">
                {term}
              </span>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="text-lg font-semibold">Possible conditions</h2>
        <div className="mt-3 space-y-3">
          {response.possible_conditions.map((item) => (
            <div key={item.name} className="rounded-3xl bg-surface-700 p-4">
              <div className="flex items-center justify-between gap-4">
                <p className="text-sm font-medium">{item.name}</p>
                <p className="text-sm font-semibold text-primary">{(item.confidence * 100).toFixed(1)}%</p>
              </div>
              <div className="mt-3 h-2 rounded-full bg-surface-800">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-primary to-surface-500"
                  style={{ width: `${Math.min(item.confidence * 100, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </section>

      {response.explanations && response.explanations.length > 0 && (
        <section>
          <div className="flex items-center gap-2">
            <BookOpenText className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Relevant medical logic</h2>
          </div>
          <div className="mt-3 space-y-3">
            {response.explanations.map((item, index) => (
              <article key={`${item.question}-${index}`} className="rounded-3xl border border-surface-700 bg-surface-900/50 p-4">
                <div className="flex items-center justify-between gap-4">
                  <h3 className="text-sm font-semibold">{item.question}</h3>
                  <span className="rounded-full bg-primary/20 px-3 py-1 text-xs font-medium text-primary">
                    Search Score: {item.score.toFixed(2)}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-7 text-ink-muted">{item.answer}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      <section className="rounded-3xl border border-amber-500/30 bg-amber-900/20 p-4 mt-8">
        <h2 className="text-sm font-semibold text-amber-500">Disclaimer</h2>
        <p className="mt-2 text-sm leading-7 text-amber-500/80">{response.disclaimer}</p>
      </section>
    </article>
  );
}
