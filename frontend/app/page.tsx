"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { stream_ideas_sse } from "@/lib/stream_ideas_sse";

type IdeaRecord = {
  id: number;
  topic: string;
  content: string;
};

const markdown_class =
  "text-sm text-zinc-900 dark:text-zinc-100 [&_a]:text-blue-600 [&_a]:underline dark:[&_a]:text-blue-400 [&_code]:rounded [&_code]:bg-zinc-200 [&_code]:px-1 [&_code]:py-0.5 [&_code]:font-mono [&_code]:text-[0.85em] dark:[&_code]:bg-zinc-800 [&_h1]:mt-3 [&_h1]:mb-2 [&_h1]:text-lg [&_h1]:font-semibold [&_h1]:first:mt-0 [&_h2]:mt-2 [&_h2]:mb-1 [&_h2]:text-base [&_h2]:font-semibold [&_h3]:mt-2 [&_h3]:mb-1 [&_h3]:text-sm [&_h3]:font-semibold [&_li]:my-0.5 [&_ol]:my-2 [&_ol]:list-decimal [&_ol]:pl-5 [&_p]:my-2 [&_pre]:my-2 [&_pre]:max-w-full [&_pre]:overflow-x-auto [&_pre]:rounded-lg [&_pre]:bg-zinc-900 [&_pre]:p-3 [&_pre]:text-zinc-100 [&_strong]:font-semibold [&_ul]:my-2 [&_ul]:list-disc [&_ul]:pl-5";

export default function Home() {
  const [topic, setTopic] = useState("");
  const [context, setContext] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [records, setRecords] = useState<IdeaRecord[]>([]);
  const [recordsError, setRecordsError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const loadRecords = useCallback(async () => {
    setRecordsError(null);
    try {
      const res = await fetch("/api/v1/ideas/records");
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || res.statusText);
      }
      const data = (await res.json()) as IdeaRecord[];
      setRecords(data);
    } catch (err) {
      setRecords([]);
      setRecordsError(
        err instanceof Error ? err.message : "Could not load saved ideas",
      );
    }
  }, []);

  useEffect(() => {
    void loadRecords();
  }, [loadRecords]);

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
      await loadRecords();
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
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-10 px-4 py-10 sm:px-6">
      <section className="flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            Business ideas
          </h1>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
            Streams markdown over SSE; saved to Postgres when using Docker
            Compose.
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
            <label
              htmlFor="context"
              className="mb-1 block text-sm font-medium"
            >
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
          <div>
            <h2 className="mb-2 text-sm font-medium text-zinc-600 dark:text-zinc-400">
              Latest output
            </h2>
            <section
              className={`rounded-lg border border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-800 dark:bg-zinc-900/50 ${markdown_class}`}
            >
              <ReactMarkdown>{content}</ReactMarkdown>
            </section>
          </div>
        ) : null}
      </section>

      <section className="flex flex-col gap-4 border-t border-zinc-200 pt-8 dark:border-zinc-800">
        <h2 className="text-lg font-semibold text-foreground">Saved ideas</h2>
        {recordsError ? (
          <p className="text-sm text-amber-600 dark:text-amber-400">
            {recordsError}
          </p>
        ) : null}
        {records.length === 0 && !recordsError ? (
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            No saved runs yet. Generate one above (requires database).
          </p>
        ) : null}
        <ul className="flex flex-col gap-6">
          {records.map((r) => (
            <li
              key={r.id}
              className="rounded-lg border border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-800 dark:bg-zinc-900/40"
            >
              <h3 className="mb-3 text-base font-semibold text-foreground">
                {r.topic}
              </h3>
              <div className={markdown_class}>
                <ReactMarkdown>{r.content}</ReactMarkdown>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
