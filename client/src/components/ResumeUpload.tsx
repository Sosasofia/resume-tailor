import { useState } from "react";

interface ResumeUploadProps {
    onAnalyze: (resume: File, jobDescription: string) => Promise<void>;
    loading: boolean;
}

export function ResumeUpload({ onAnalyze, loading }: ResumeUploadProps) {
    const [resume, setResume] = useState<File | null>(null);
    const [jobDescription, setJobDescription] = useState("");
    const [error, setError] = useState("");

    async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();
        setError("");

        if (!resume) {
            setError("Please upload your resume.");
            return;
        }

        if (!jobDescription.trim()) {
            setError("Please enter the job description.");
            return;
        }

        try {
            await onAnalyze(resume, jobDescription);
        } catch (error) {
            setError(error instanceof Error ? error.message : "Failed to analyze resume.");
        }
    }

    return (
        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 p-4 bg-gray-50 flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                <h2 className="font-bold uppercase tracking-wide">Original Resume</h2>
            </div>

            <form onSubmit={handleSubmit} className="flex flex-col gap-6 p-6">
                <div className="flex flex-col gap-2">
                    <label htmlFor="resume" className="text-sm font-semibold text-slate-800">
                        Upload Document (PDF)
                    </label>
                    <input
                        id="resume"
                        type="file"
                        accept=".pdf,application/pdf"
                        onChange={(event) => setResume(event.target.files?.[0] ?? null)}
                        disabled={loading}
                        className="w-full rounded-lg border border-dashed border-slate-300 bg-slate-50 p-3 text-sm text-slate-600 file:mr-4 file:cursor-pointer file:rounded-md file:border-0 file:bg-blue-600 file:px-3 file:py-2 file:font-semibold file:text-white hover:file:bg-blue-700"
                    />
                </div>

                <div className="flex items-center gap-3 py-1">
                    <div className="h-px flex-1 bg-slate-200"></div>
                    <span className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">Job Description</span>
                    <div className="h-px flex-1 bg-slate-200"></div>
                </div>

                <div className="flex flex-col gap-2">
                    <textarea
                        id="job-description"
                        rows={10}
                        value={jobDescription}
                        onChange={(event) => setJobDescription(event.target.value)}
                        placeholder="Paste the job description here..."
                        disabled={loading}
                        className="w-full resize-y rounded-lg border border-slate-300 p-3 text-sm text-slate-800 outline-none placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    />
                </div>

                {error && (
                    <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm font-medium text-red-700">
                        {error}
                    </div>
                )}

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    {loading ? "Analyzing..." : "Analyze Match"}
                </button>
            </form>
        </div>
    );
}