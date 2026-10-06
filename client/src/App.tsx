import { useState } from "react";
import {
  analyzeResume,
  tailorResume,
} from "./api/client";

import { AnalysisResult } from "./components/AnalysisResult";
import { ResumeUpload } from "./components/ResumeUpload";
import type { ResumeAnalysis } from "./types/api";

function App() {
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [resume, setResume] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [tailoring, setTailoring] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze(
    selectedResume: File,
    selectedJobDescription: string,
  ) {
    setLoading(true);
    setError(null);
    setAnalysis(null);

    setResume(selectedResume);
    setJobDescription(selectedJobDescription);

    try {
      const result = await analyzeResume(
        selectedResume,
        selectedJobDescription,
      );

      setAnalysis(result);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to analyze resume.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleTailor() {
    if (!resume) {
      return;
    }

    setTailoring(true);
    setError(null);

    try {
      const pdf = await tailorResume(
        resume,
        jobDescription,
      );

      const url = URL.createObjectURL(pdf);

      const link = document.createElement("a");

      link.href = url;
      link.download = "tailored_resume.pdf";

      document.body.appendChild(link);
      link.click();
      link.remove();

      URL.revokeObjectURL(url);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to tailor resume.",
      );
    } finally {
      setTailoring(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 px-5 py-8 font-sans text-slate-950 sm:px-8 lg:px-12 lg:py-12">
      <header className="mx-auto mb-10 max-w-7xl text-center">
        <p className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-blue-700">
          Resume intelligence
        </p>
        <h1 className="mb-3 text-3xl font-semibold tracking-tight sm:text-4xl">
          AI Resume Tailor
        </h1>
        <p className="mx-auto max-w-2xl text-base text-slate-600">
          Analyze your resume against a job description before tailoring it.
        </p>
      </header>

      <main className="mx-auto grid max-w-7xl grid-cols-1 items-start gap-6 lg:grid-cols-12">
        <div className="lg:col-span-4">
          <ResumeUpload onAnalyze={handleAnalyze} loading={loading} />
        </div>

        <div className="lg:col-span-8">
          {analysis ? (
            <AnalysisResult
              analysis={analysis}
              onTailor={handleTailor}
              tailoring={tailoring}
            />
          ) : (
            <section className="flex min-h-[420px] flex-col items-center justify-center rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
              <div className="mb-5 rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">
                Awaiting analysis
              </div>
              <h2 className="mb-3 text-2xl font-semibold tracking-tight sm:text-3xl">
                Your match report will appear here
              </h2>
              <p className="max-w-md text-slate-500">
                Upload your resume and paste a job description to compare your
                experience with the role requirements.
              </p>
            </section>
          )}

          {error && (
            <div
              role="alert"
              className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
            >
              {error}
            </div>
          )}
        </div>

      </main>
    </div>
  );
}

export default App;