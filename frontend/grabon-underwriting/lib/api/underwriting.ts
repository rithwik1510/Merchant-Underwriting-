import { apiFetch } from "./client";
import { UnderwritingRun, UnderwritingRunListItem } from "../types/underwriting";

export const runUnderwriting = (merchantId: string) =>
  apiFetch<UnderwritingRun>(`/underwriting/run/${merchantId}`, {
    method: "POST",
  });

export const getUnderwritingRuns = () =>
  apiFetch<UnderwritingRunListItem[]>("/underwriting/runs");

export const getUnderwritingRun = (runId: number | string) =>
  apiFetch<UnderwritingRun>(`/underwriting/runs/${runId}`);
