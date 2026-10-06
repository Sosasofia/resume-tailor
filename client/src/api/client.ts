import type { ResumeAnalysis } from "../types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function analyzeResume(
  resume: File,
  jobDescription: string,
): Promise<ResumeAnalysis> {
  const formData = new FormData();

  formData.append("resume", resume);
  formData.append(
    "job_description_text",
    jobDescription,
  );

  const response = await fetch(
    `${API_BASE_URL}/analyze`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    const errorBody = await response.json().catch(
      () => null,
    );

    throw new Error(
      typeof errorBody?.detail === "string"
        ? errorBody.detail
        : "Failed to analyze resume.",
    );
  }

  return response.json();
}

export async function tailorResume(
  resume: File,
  jobDescription: string,
): Promise<Blob> {
  const formData = new FormData();

  formData.append("format", "pdf");
  formData.append("resume", resume);
  formData.append(
    "job_description_text",
    jobDescription,
  );

  const response = await fetch(
    `${API_BASE_URL}/tailor`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    const errorBody = await response.json().catch(
      () => null,
    );

    const detail = errorBody?.detail;

    if (typeof detail === "string") {
      throw new Error(detail);
    }

    if (detail?.stage) {
      throw new Error(
        `Resume validation failed during ${detail.stage}.`,
      );
    }

    throw new Error("Failed to tailor resume.");
  }

  return response.blob();
}