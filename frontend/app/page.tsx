import Link from "next/link";
import { ArrowRight, ShieldAlert, Stethoscope } from "lucide-react";

export default function HomePage() {
  return (
    <main className="medical-grid min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-6xl flex-col justify-center">
        <div className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
          <section className="space-y-8">
            <div className="inline-flex items-center gap-2 rounded-full border border-teal/15 bg-white/80 px-4 py-2 text-sm font-medium text-teal shadow-panel">
              <Stethoscope className="h-4 w-4" />
              MedAssist AI
            </div>
            <div className="space-y-4">
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-slateblue sm:text-5xl lg:text-6xl">
                AI-powered symptom guidance with medical knowledge retrieval
              </h1>
              <p className="max-w-2xl text-base leading-7 text-slateblue/80 sm:text-lg">
                Describe symptoms in plain language and get safety-first educational guidance,
                ranked possible conditions, and related medical Q&amp;A context from MedQuAD.
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Link
                href="/chat"
                className="inline-flex items-center justify-center gap-2 rounded-2xl bg-teal px-6 py-3 text-sm font-semibold text-white transition hover:bg-slateblue"
              >
                Start Chat
                <ArrowRight className="h-4 w-4" />
              </Link>
              <a
                href="#safety"
                className="inline-flex items-center justify-center rounded-2xl border border-slateblue/15 bg-white px-6 py-3 text-sm font-semibold text-slateblue transition hover:border-teal/40 hover:text-teal"
              >
                Review Safety Notes
              </a>
            </div>
          </section>

          <section className="rounded-[2rem] border border-teal/10 bg-white/90 p-6 shadow-panel backdrop-blur">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 rounded-full bg-red-50 px-3 py-1 text-sm font-medium text-red-700">
                <ShieldAlert className="h-4 w-4" />
                Safety-first use only
              </div>
              <h2 className="text-2xl font-semibold text-slateblue">Important medical disclaimer</h2>
              <p className="text-sm leading-7 text-slateblue/80">
                MedAssist AI does not provide a final diagnosis and should not replace licensed
                medical care. If you have chest pain, trouble breathing, severe bleeding,
                unconsciousness, seizure, stroke symptoms, or thoughts of self-harm, seek urgent
                help immediately.
              </p>
              <div className="rounded-2xl bg-mist p-4 text-sm leading-7 text-slateblue/80">
                Outputs are intended to help you prepare for a discussion with a clinician. Always
                consult a qualified healthcare professional for diagnosis and treatment.
              </div>
            </div>
          </section>
        </div>

        <section id="safety" className="mt-12 grid gap-4 md:grid-cols-3">
          {[
            {
              title: "Educational support",
              body: "The chatbot ranks possible conditions using a baseline symptom classifier. It never confirms disease.",
            },
            {
              title: "Medical knowledge retrieval",
              body: "MedQuAD passages add practical context, explanations, and next-step guidance instead of acting as a diagnosis engine.",
            },
            {
              title: "Emergency escalation",
              body: "Red-flag symptom detection prioritizes warnings for emergency evaluation before anything else.",
            },
          ].map((card) => (
            <article
              key={card.title}
              className="rounded-3xl border border-slateblue/10 bg-white/85 p-5 shadow-panel"
            >
              <h3 className="text-lg font-semibold text-slateblue">{card.title}</h3>
              <p className="mt-2 text-sm leading-7 text-slateblue/75">{card.body}</p>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}
