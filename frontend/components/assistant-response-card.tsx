import { AlertTriangle, BookOpenText, ShieldPlus } from "lucide-react";

import type { ChatResponse } from "@/types/api";

export function AssistantResponseCard({ response }: { response: ChatResponse }) {
  return (
    <article className="space-y-4 rounded-[1.75rem] border border-slateblue/10 bg-white p-4 shadow-panel sm:p-6">
      {response.emergency ? (
        <div className="rounded-3xl border border-red-200 bg-red-50 p-4 text-red-800">
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
        <h2 className="text-lg font-semibold text-slateblue">Assistant response</h2>
        <p className="mt-2 whitespace-pre-line text-sm leading-7 text-slateblue/80">
          {response.assistant_response}
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-slateblue">Possible conditions</h2>
        <div className="mt-3 space-y-3">
          {response.possible_conditions.map((item) => (
            <div key={item.condition} className="rounded-3xl bg-mist p-4">
              <div className="flex items-center justify-between gap-4">
                <p className="text-sm font-medium text-slateblue">{item.condition}</p>
                <p className="text-sm font-semibold text-teal">{item.confidence.toFixed(1)}%</p>
              </div>
              <div className="mt-3 h-2 rounded-full bg-white">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-teal to-slateblue"
                  style={{ width: `${Math.min(item.confidence, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <div className="flex items-center gap-2">
          <BookOpenText className="h-5 w-5 text-teal" />
          <h2 className="text-lg font-semibold text-slateblue">Helpful medical information</h2>
        </div>
        <div className="mt-3 space-y-3">
          {response.knowledge_summary.map((item, index) => (
            <article key={`${item.question}-${index}`} className="rounded-3xl border border-slateblue/10 p-4">
              <div className="flex items-center justify-between gap-4">
                <h3 className="text-sm font-semibold text-slateblue">{item.question}</h3>
                <span className="rounded-full bg-teal/10 px-3 py-1 text-xs font-medium text-teal">
                  {item.score.toFixed(2)}
                </span>
              </div>
              <p className="mt-2 text-sm leading-7 text-slateblue/75">{item.answer}</p>
              <p className="mt-2 text-xs uppercase tracking-[0.2em] text-slateblue/45">
                {item.source}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-3xl bg-mist p-4">
          <h2 className="text-sm font-semibold text-slateblue">Suggested next steps</h2>
          <ul className="mt-3 space-y-2 text-sm leading-7 text-slateblue/75">
            {response.suggested_next_steps.map((item) => (
              <li key={item}>- {item}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-3xl bg-slateblue p-4 text-white">
          <div className="flex items-center gap-2">
            <ShieldPlus className="h-5 w-5" />
            <h2 className="text-sm font-semibold">When to seek urgent care</h2>
          </div>
          <ul className="mt-3 space-y-2 text-sm leading-7 text-white/85">
            {response.urgent_care_reasons.map((item) => (
              <li key={item}>- {item}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="rounded-3xl border border-amber-200 bg-amber-50 p-4">
        <h2 className="text-sm font-semibold text-amber-900">Disclaimer</h2>
        <p className="mt-2 text-sm leading-7 text-amber-900/80">{response.disclaimer}</p>
      </section>
    </article>
  );
}
