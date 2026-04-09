"use client";

import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { stream_ideas_sse } from "@/lib/stream_ideas_sse";

export default function Home() {
  const [topic, setTopic] = useState("");
  const [context, setContext] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    abortRef.current?.abort();
    abortRef.current = new AbortController();
    const { signal } = abortRef.current;

    setError(null);
    setContent("");
    setLoading(true);
    try {
      await stream_ideas_sse(
        "/api/v1/ideas/stream",
        {
          topic: topic.trim(),
          context: context.trim() || null,
        },
        signal,
        (text) => {
          setContent((prev) => prev + text);
        },
      );
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        return;
      }
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-xl flex-col gap-6 px-4 py-10 sm:px-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Business ideas
        </h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          Streams markdown over SSE from{" "}
          <code className="rounded bg-zinc-200 px-1 py-0.5 text-xs dark:bg-zinc-800">
            POST /api/v1/ideas/stream
          </code>
          . Run FastAPI on port 8000 with{" "}
          <code className="rounded bg-zinc-200 px-1 py-0.5 text-xs dark:bg-zinc-800">
            npm run dev
          </code>
          .
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label htmlFor="topic" className="mb-1 block text-sm font-medium">
            Topic
          </label>
          <input
            id="topic"
            className="w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 outline-none ring-blue-500 focus:ring-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. B2B tools for small veterinary clinics"
            required
            autoComplete="off"
          />
        </div>
        <div>
          <label htmlFor="context" className="mb-1 block text-sm font-medium">
            Context (optional)
          </label>
          <textarea
            id="context"
            className="min-h-[7rem] w-full resize-y rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 outline-none ring-blue-500 focus:ring-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Audience, region, constraints…"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Streaming…" : "Generate"}
        </button>
      </form>

      {error ? (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      ) : null}

      {content ? (
        <section
          className="rounded-lg border border-zinc-200 bg-zinc-50 p-4 text-sm text-zinc-900 dark:border-zinc-800 dark:bg-zinc-900/50 dark:text-zinc-100 [&_a]:text-blue-600 [&_a]:underline dark:[&_a]:text-blue-400 [&_code]:rounded [&_code]:bg-zinc-200 [&_code]:px-1 [&_code]:py-0.5 [&_code]:font-mono [&_code]:text-[0.85em] dark:[&_code]:bg-zinc-800 [&_h1]:mt-4 [&_h1]:mb-2 [&_h1]:text-xl [&_h1]:font-semibold [&_h1]:first:mt-0 [&_h2]:mt-3 [&_h2]:mb-2 [&_h2]:text-lg [&_h2]:font-semibold [&_h3]:mt-2 [&_h3]:mb-1 [&_h3]:text-base [&_h3]:font-semibold [&_li]:my-0.5 [&_ol]:my-2 [&_ol]:list-decimal [&_ol]:pl-5 [&_p]:my-2 [&_pre]:my-2 [&_pre]:max-w-full [&_pre]:overflow-x-auto [&_pre]:rounded-lg [&_pre]:bg-zinc-900 [&_pre]:p-3 [&_pre]:text-zinc-100 [&_strong]:font-semibold [&_ul]:my-2 [&_ul]:list-disc [&_ul]:pl-5"
        >
          <ReactMarkdown>{content}</ReactMarkdown>
        </section>
      ) : null}
    </main>
  );
}
