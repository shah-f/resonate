"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    const data = new FormData(e.currentTarget);
    const res = await fetch("/api/analyze", { method: "POST", body: data });
    const { jobId } = await res.json();
    router.push(`/results/${jobId}`);
  }

  return (
    /* Esha: replace this entire <main> with your upload component */
    <main className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-2xl font-bold">Resonate</h1>
      <p className="text-gray-400">Find the moments your video loses the brain.</p>
      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
        <input
          name="video"
          type="file"
          accept=".mp4,.mov,.webm"
          required
          className="block"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 rounded disabled:opacity-50"
        >
          {loading ? "Uploading..." : "Analyze Video"}
        </button>
      </form>
    </main>
  );
}
