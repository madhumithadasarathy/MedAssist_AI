import { AlertTriangle, BookOpenText, ShieldPlus } from "lucide-react";

import type { ChatResponse } from "@/types/api";

export function AssistantResponseCard({ response }: { response: ChatResponse }) {
  return (
    <article className="space-y-4 rounded-[1.75rem] border border-surface-700 bg-surface-800 p-4 shadow-panel sm:p-6">
      {response.emergency ? (
        <div className="rounded-3xl border border-red-500/30 bg-red-900/20 p-4 text-red-400">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
            <div>
              <h2 className="font-semibold">Emergency warning</h2>
              <p className="mt-1 text-sm leading-7">
                Red-flag symptoms were detected. Seek immediate medical help or contact local
                emergency services right away.
              </p>
            </div>
          </div>
        </div>
      ) : null}

      <section>
        <h2 className="text-lg font-semibold text-ink">Assistant response</h2>
        <p className="mt-2 whitespace-pre-line text-sm leading-7 text-ink-muted">
          {response.assistant_response}
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-ink">Possible conditions</h2>
        <div className="mt-3 space-y-3">
          {response.possible_conditions.map((item) => (
            <div key={item.condition} className="rounded-3xl bg-surface-700 p-4">
              <div className="flex items-center justify-between gap-4">
                <p className="text-sm font-medium text-ink">{item.condition}</p>
                <p className="text-sm font-semibold text-primary">{item.confidence.toFixed(1)}%</p>
              </div>
              <div className="mt-3 h-2 rounded-full bg-surface-800">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-primary to-surface-500"
                  style={{ width: `${Math.min(item.confidence, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <div className="flex items-center gap-2">
          <BookOpenText className="h-5 w-5 text-primary" />
          <h2 className="text-lg font-semibold text-ink">Helpful medical information</h2>
        </div>
        <div className="mt-3 space-y-3">
          {response.knowledge_summary.map((item, index) => (
            <article key={`${item.question}-${index}`} className="rounded-3xl border border-surface-700 bg-surface-900/50 p-4">
              <div className="flex items-center justify-between gap-4">
                <h3 className="text-sm font-semibold text-ink">{item.question}</h3>
                <span className="rounded-full bg-primary/20 px-3 py-1 text-xs font-medium text-primary">
                  {item.score.toFixed(2)}
                </span>
              </div>
              <p className="mt-2 text-sm leading-7 text-ink-muted">{item.answer}</p>
              <p className="mt-2 text-xs uppercase tracking-[0.2em] text-surface-500">
                {item.source}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-3xl bg-surface-700 p-4">
          <h2 className="text-sm font-semibold text-ink">Suggested next steps</h2>
          <ul className="mt-3 space-y-2 text-sm leading-7 text-ink-muted">
            {response.suggested_next_steps.map((item) => (
              <li key={item}>- {item}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-3xl bg-surface-900 p-4 text-ink">
          <div className="flex items-center gap-2">
            <ShieldPlus className="h-5 w-5 text-red-400" />
            <h2 className="text-sm font-semibold text-red-500">When to seek urgent care</h2>
          </div>
          <ul className="mt-3 space-y-2 text-sm leading-7 text-ink-muted">
            {response.urgent_care_reasons.map((item) => (
              <li key={item}>- {item}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="rounded-3xl border border-amber-500/30 bg-amber-900/20 p-4">
        <h2 className="text-sm font-semibold text-amber-500">Disclaimer</h2>
        <p className="mt-2 text-sm leading-7 text-amber-500/80">{response.disclaimer}</p>
      </section>
    </article>
  );
}
