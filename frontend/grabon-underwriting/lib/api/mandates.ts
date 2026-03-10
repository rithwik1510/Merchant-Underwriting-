import { apiFetch } from "./client";
import { MandateSession } from "../types/mandates";

export const startMandate = (
  runId: number | string,
  body: { account_holder_name: string; mobile_number: string }
) =>
  apiFetch<MandateSession>(`/mandates/${runId}/start`, {
    method: "POST",
    body: JSON.stringify(body),
  });

export const selectBank = (
  runId: number | string,
  body: { bank_name: string; account_number: string; ifsc_code: string }
) =>
  apiFetch<MandateSession>(`/mandates/${runId}/select-bank`, {
    method: "POST",
    body: JSON.stringify(body),
  });

export const sendOtp = (runId: number | string) =>
  apiFetch<MandateSession>(`/mandates/${runId}/send-otp`, {
    method: "POST",
  });

export const verifyOtp = (runId: number | string, body: { otp: string }) =>
  apiFetch<MandateSession>(`/mandates/${runId}/verify-otp`, {
    method: "POST",
    body: JSON.stringify(body),
  });

export const completeMandate = (runId: number | string) =>
  apiFetch<MandateSession>(`/mandates/${runId}/complete`, {
    method: "POST",
  });

export const getMandateStatus = (runId: number | string) =>
  apiFetch<MandateSession>(`/mandates/${runId}`);
