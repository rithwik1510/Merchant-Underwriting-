import { apiFetch } from "./client";
import { OfferAcceptanceRequest, OfferAcceptanceResponse, Phase4ResetResponse } from "../types/offers";

export const acceptOffer = (runId: number | string, body: OfferAcceptanceRequest) =>
  apiFetch<OfferAcceptanceResponse>(`/offers/${runId}/accept`, {
    method: "POST",
    body: JSON.stringify(body),
  });

export const getAcceptance = (runId: number | string) =>
  apiFetch<OfferAcceptanceResponse>(`/offers/${runId}/acceptance`);

export const resetPhase4Demo = (runId: number | string) =>
  apiFetch<Phase4ResetResponse>(`/offers/${runId}/reset-demo`, {
    method: "POST",
  });
