import type { ExperimentRunResponse, RunExperimentInput } from "../types";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

export async function runExperiment(
  input: RunExperimentInput,
): Promise<ExperimentRunResponse> {
  const formData = new FormData();
  formData.append("file", input.file);
  formData.append("objective", input.objective);
  formData.append("target_column", input.targetColumn);
  formData.append("max_experiments", String(input.maxExperiments));

  const response = await fetch(`${API_BASE_URL}/api/experiments/run`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let detail = "The experiment could not be completed.";
    try {
      const payload = (await response.json()) as { detail?: string };
      detail = payload.detail ?? detail;
    } catch {
      // Keep a useful generic message when the backend did not return JSON.
    }
    throw new Error(detail);
  }

  return (await response.json()) as ExperimentRunResponse;
}
