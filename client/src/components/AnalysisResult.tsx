import type { ResumeAnalysis } from "../types/api";

interface AnalysisResultProps {
    analysis: ResumeAnalysis;
    onTailor: () => Promise<void>;
    tailoring: boolean;
}

export function AnalysisResult({ analysis, onTailor, tailoring }: AnalysisResultProps) {
    return (
        <div className="flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-200 p-5">
                <div>
                    <p className="mb-1 text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">Analysis</p>
                    <h2 className="text-lg font-semibold text-slate-900">ATS match report</h2>
                </div>
                <button
                    type="button"
                    onClick={onTailor}
                    disabled={tailoring}
                    className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-slate-700 disabled:opacity-50"
                >
                    {tailoring ? "Generating..." : "Tailor my resume"}
                </button>
            </div>

            <div className="flex-grow p-5 lg:p-8">
                <div className="font-sans">
                    <div className="mb-8 border-b border-slate-200 pb-5">
                        <p className="mb-2 text-sm font-medium text-slate-500">Overall match</p>
                        <h3 className="text-4xl font-semibold tracking-tight text-slate-900">
                            <span className={analysis.match_score > 70 ? "text-emerald-600" : "text-amber-600"}>{analysis.match_score}%</span>
                        </h3>
                    </div>

                    <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
                        <div>
                            <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.12em] text-slate-500">Matching skills</h3>
                            {analysis.matching_skills.length > 0 ? (
                                <ul className="list-disc pl-5 space-y-1">
                                    {analysis.matching_skills.map((skill) => (
                                        <li key={skill} className="text-slate-700">{skill}</li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="text-sm text-slate-500">No matching required skills.</p>
                            )}
                        </div>

                        <div>
                            <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.12em] text-slate-500">Missing skills</h3>
                            {analysis.missing_required_skills.length > 0 ? (
                                <ul className="list-disc pl-5 space-y-1">
                                    {analysis.missing_required_skills.map((skill) => (
                                        <li key={skill} className="text-red-600">{skill}</li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="text-sm text-slate-500">No missing required skills.</p>
                            )}
                        </div>

                        <div className="md:col-span-2">
                            <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.12em] text-slate-500">Recommendations</h3>
                            {analysis.recommendations.length > 0 ? (
                                <ul className="space-y-2">
                                    {analysis.recommendations.map((recommendation) => (
                                        <li key={recommendation} className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-slate-700">
                                            {recommendation}
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="text-sm text-slate-500">No recommendations.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}