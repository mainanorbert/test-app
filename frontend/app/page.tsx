"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { stream_ideas_sse } from "@/lib/stream_ideas_sse";

type ChatTurn = { role: "user" | "assistant"; content: string };

const SUGGESTED_PROMPTS = [
  "What's your strongest technical stack?",
  "Tell me about your AI and LLM work.",
  "How do you approach mentoring or leading developers?",
];

export default function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatTurn[]>([]);
  const [streaming, setStreaming] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streaming]);

  /**
   * Sends a user message to the career chat stream and appends the assistant reply.
   */
  async function send_message(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    abortRef.current?.abort();
    abortRef.current = new AbortController();
    const { signal } = abortRef.current;

    setError(null);
    setLoading(true);
    setStreaming("");
    setInput("");

    const historySnapshot = messages;
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);

    let assistant = "";
    try {
      await stream_ideas_sse(
        "/api/v1/career/chat/stream",
        { message: trimmed, history: historySnapshot },
        signal,
        (delta) => {
          assistant += delta;
          setStreaming(assistant);
        },
      );
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: assistant },
      ]);
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        setMessages((prev) => prev.slice(0, -1));
        return;
      }
      setError(err instanceof Error ? err.message : "Request failed");
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setStreaming("");
      setLoading(false);
    }
  }

  /**
   * Handles the chat form submission event.
   */
  function handle_submit(e: React.FormEvent) {
    e.preventDefault();
    void send_message(input);
  }

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-[#080f1e]">
      {/* Ambient background */}
      <div className="pointer-events-none fixed inset-0 bg-aurora" />
      <div className="pointer-events-none fixed inset-0 bg-grid" />
      <div className="pointer-events-none fixed -left-40 -top-20 h-[600px] w-[600px] rounded-full bg-[#1e5bff]/10 blur-[140px]" />
      <div className="pointer-events-none fixed right-[-12rem] top-60 h-[400px] w-[400px] rounded-full bg-[#4f86ff]/8 blur-[100px]" />
      <div className="pointer-events-none fixed bottom-0 left-1/2 h-80 w-[700px] -translate-x-1/2 rounded-full bg-[#1e5bff]/6 blur-[100px]" />

      {/* ── NAVBAR ── */}
      <header className="navbar-glass sticky top-0 z-50 border-b border-white/[0.07]">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <a href="/" className="group flex items-center gap-3">
            <div className="relative h-10 w-10 shrink-0 overflow-hidden rounded-full border-2 border-[#4f86ff]/60 shadow-[0_0_18px_rgba(79,134,255,0.4)] transition group-hover:shadow-[0_0_28px_rgba(79,134,255,0.55)]">
              <Image
                src="/nober.jpg"
                alt="Norbert"
                width={80}
                height={80}
                className="h-full w-full object-cover object-top"
                priority
              />
            </div>
            <div>
              <p className="text-sm font-semibold leading-none text-white">
                Norbert Osiemo
              </p>
              <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-widest text-[#4f86ff]">
                AI Engineer · Builder
              </p>
            </div>
          </a>

          <nav className="flex items-center gap-2">
            <a
              href="#chat"
              className="rounded-full bg-[#4f86ff] px-4 py-1.5 text-[11px] font-bold uppercase tracking-widest text-white shadow-[0_0_18px_rgba(79,134,255,0.45)] transition hover:bg-[#3a6fe8] hover:shadow-[0_0_26px_rgba(79,134,255,0.55)]"
            >
              Chat
            </a>
            <a
              href="https://www.linkedin.com/in/norbert-osiemo-0256a4144/"
              target="_blank"
              rel="noreferrer"
              className="rounded-full border border-white/15 px-4 py-1.5 text-[11px] font-semibold uppercase tracking-widest text-white/65 transition hover:border-white/35 hover:text-white"
            >
              LinkedIn
            </a>
            <a
              href="https://github.com/mainanorbert"
              target="_blank"
              rel="noreferrer"
              className="rounded-full border border-white/15 px-4 py-1.5 text-[11px] font-semibold uppercase tracking-widest text-white/65 transition hover:border-white/35 hover:text-white"
            >
              GitHub
            </a>
          </nav>
        </div>
      </header>

      {/* ── MAIN ── */}
      <main className="relative mx-auto max-w-5xl px-4 pb-20 sm:px-6">
        {/* ── HERO ── */}
        <section className="pb-10 pt-12 lg:pt-16">
          <div className="flex flex-col gap-10 lg:flex-row lg:items-start lg:justify-between">
            {/* Left: intro text */}
            <div className="max-w-xl animate-fade-up">
              <span className="inline-flex items-center gap-1.5 rounded-full border border-[#4f86ff]/30 bg-[#4f86ff]/10 px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-[#4f86ff]">
                Portfolio · Career Beacon
              </span>
              <h1 className="mt-5 text-4xl font-bold leading-tight tracking-tight text-white sm:text-5xl">
                Building AI products, leading teams &amp; shipping thoughtful
                software.
              </h1>
              <p className="mt-4 text-base leading-relaxed text-white/60">
                I blend product sense with engineering depth — AI-first
                experiences, scalable backend systems, and mentoring builders.
                This is a living portfolio plus a chat interface that speaks in
                my voice.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <a
                  href="mailto:norbert@example.com"
                  className="rounded-full bg-[#4f86ff] px-5 py-2.5 text-sm font-semibold text-white shadow-[0_0_22px_rgba(79,134,255,0.4)] transition hover:opacity-90"
                >
                  Start a Conversation
                </a>
                <a
                  href="#chat"
                  className="rounded-full border border-white/15 px-5 py-2.5 text-sm font-semibold text-white/70 transition hover:border-white/35 hover:text-white"
                >
                  Chat with Me ↓
                </a>
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                {[
                  "AI Product",
                  "Backend",
                  "Growth Experiments",
                  "Mentorship",
                ].map((chip) => (
                  <span
                    key={chip}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[10px] font-semibold uppercase tracking-widest text-white/45"
                  >
                    {chip}
                  </span>
                ))}
              </div>
            </div>

            {/* Right: portrait + stats */}
            <div className="flex shrink-0 animate-fade-up flex-col items-center gap-6 lg:items-end">
              <div className="relative">
                <div className="h-52 w-44 overflow-hidden rounded-3xl border border-[#4f86ff]/35 shadow-[0_0_60px_rgba(79,134,255,0.2),0_24px_64px_rgba(0,0,0,0.6)]">
                  <Image
                    src="/nober.jpg"
                    alt="Portrait of Norbert Osiemo"
                    width={352}
                    height={416}
                    className="h-full w-full object-cover object-top"
                    priority
                  />
                </div>
                <span className="absolute -bottom-3.5 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-full border border-green-500/40 bg-[#080f1e] px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-green-400 shadow-[0_0_14px_rgba(74,222,128,0.22)]">
                  ● Available
                </span>
              </div>

              <div className="mt-2 grid grid-cols-3 gap-3 lg:grid-cols-1 lg:w-44">
                {[
                  { label: "6+ yrs", desc: "Engineering & leadership" },
                  { label: "LLM", desc: "Product + research" },
                  { label: "Global", desc: "Remote teams & clients" },
                ].map((item) => (
                  <div
                    key={item.label}
                    className="rounded-2xl border border-white/8 bg-white/4 px-4 py-3 text-center backdrop-blur-sm lg:text-left"
                  >
                    <p className="text-lg font-bold text-white">{item.label}</p>
                    <p className="text-[10px] text-white/40">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ── CHAT — CENTERPIECE ── */}
        <section
          id="chat"
          className="chat-centerpiece overflow-hidden rounded-3xl"
        >
          {/* Chat header */}
          <div className="border-b border-white/[0.07] bg-gradient-to-r from-[#4f86ff]/12 to-transparent px-6 py-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-bold uppercase tracking-[0.3em] text-white">
                  Chat with Norbert
                </h2>
                <p className="mt-1 text-xs text-white/45">
                  Ask about experience, projects, or leadership style. I am here to help you explore.
                </p>
              </div>
              <span className="flex items-center gap-1.5 rounded-full border border-[#4f86ff]/30 bg-[#4f86ff]/12 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.25em] text-[#4f86ff]">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[#4f86ff] shadow-[0_0_8px_rgba(79,134,255,0.9)]" />
                Live
              </span>
            </div>
          </div>

          {/* Messages area */}
          <div className="flex max-h-[min(36rem,65vh)] min-h-96 flex-col gap-4 overflow-y-auto px-6 py-6">
            {messages.length === 0 && !streaming ? (
              <div className="flex flex-col items-center justify-center gap-6 py-8 text-center">
                <div className="relative h-16 w-16 overflow-hidden rounded-full border-2 border-[#4f86ff]/50 shadow-[0_0_24px_rgba(79,134,255,0.3)]">
                  <Image
                    src="/nober.jpg"
                    alt="Norbert"
                    width={64}
                    height={64}
                    className="h-full w-full object-cover object-top"
                  />
                </div>
                <div>
                  <p className="text-sm font-medium text-white/75">
                    Pick a starter question or say hello — I&apos;ll introduce
                    myself and we can go from there.
                  </p>
                  <div className="mt-4 flex flex-wrap justify-center gap-2">
                    {SUGGESTED_PROMPTS.map((p) => (
                      <button
                        key={p}
                        type="button"
                        disabled={loading}
                        onClick={() => void send_message(p)}
                        className="rounded-full border border-white/12 bg-white/5 px-4 py-2 text-xs font-medium text-white/65 transition hover:border-[#4f86ff]/40 hover:bg-[#4f86ff]/10 hover:text-white disabled:opacity-40"
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : null}

            {messages.map((m, i) => (
              <div
                key={`${m.role}-${i}-${m.content.slice(0, 12)}`}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={
                    m.role === "user"
                      ? "max-w-[80%] rounded-3xl rounded-br-lg bg-[#4f86ff] px-5 py-3.5 text-sm leading-relaxed text-white shadow-[0_4px_20px_rgba(79,134,255,0.3)]"
                      : "max-w-[88%] rounded-3xl rounded-bl-lg border border-white/10 bg-white/5 px-5 py-3.5 text-sm leading-relaxed text-white/80 backdrop-blur-sm [&_a]:text-[#4f86ff] [&_a]:underline [&_code]:rounded [&_code]:bg-white/10 [&_code]:px-1 [&_code]:text-[0.85em] [&_li]:my-1 [&_p]:my-2 [&_strong]:font-semibold [&_strong]:text-white [&_ul]:list-disc [&_ul]:pl-4"
                  }
                >
                  {m.role === "user" ? (
                    m.content
                  ) : (
                    <ReactMarkdown>{m.content}</ReactMarkdown>
                  )}
                </div>
              </div>
            ))}

            {streaming ? (
              <div className="flex justify-start">
                <div className="max-w-[88%] rounded-3xl rounded-bl-lg border border-dashed border-[#4f86ff]/25 bg-white/5 px-5 py-3.5 text-sm leading-relaxed text-white/75 backdrop-blur-sm [&_a]:text-[#4f86ff] [&_a]:underline [&_code]:rounded [&_code]:bg-white/10 [&_code]:px-1 [&_p]:my-2">
                  <ReactMarkdown>{streaming}</ReactMarkdown>
                  <span className="ml-0.5 inline-block h-2 w-2 animate-pulse rounded-full bg-[#4f86ff] align-middle" />
                </div>
              </div>
            ) : null}

            <div ref={bottomRef} />
          </div>

          {/* Input bar */}
          <form
            onSubmit={handle_submit}
            className="flex flex-col gap-2 border-t border-white/[0.07] px-6 py-4"
          >
            {error ? (
              <p className="text-xs text-red-400">{error}</p>
            ) : null}
            <div className="flex gap-2">
              <input
                className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none ring-[#4f86ff]/30 transition placeholder:text-white/30 focus:border-[#4f86ff]/50 focus:bg-white/8 focus:ring-2"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about experience, stack, projects…"
                disabled={loading}
                autoComplete="off"
                aria-label="Your message"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="shrink-0 rounded-2xl bg-[#4f86ff] px-5 py-3 text-sm font-semibold text-white shadow-[0_0_18px_rgba(79,134,255,0.35)] transition hover:bg-[#3a6fe8] hover:shadow-[0_0_28px_rgba(79,134,255,0.5)] disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading ? "…" : "Send"}
              </button>
            </div>
          </form>
        </section>

        {/* ── HIGHLIGHTS ── */}
        <section className="mt-8 grid gap-5 sm:grid-cols-3">
          {[
            "Architected LLM-driven onboarding flows that cut activation time by 38%.",
            "Scaled cross-region data services for a fintech serving 1M+ users.",
            "Led squads of designers and engineers across Africa and Europe.",
          ].map((item, i) => (
            <div
              key={i}
              className="rounded-2xl border border-white/8 bg-white/4 px-5 py-5 backdrop-blur-sm"
            >
              <span className="mb-3 block h-1 w-8 rounded-full bg-[#4f86ff]" />
              <p className="text-sm leading-relaxed text-white/60">{item}</p>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}
