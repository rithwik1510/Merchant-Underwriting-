import { apiFetch } from "./client";
import {
  ExplanationContent,
  WhatsAppMessage,
  CommunicationsResponse,
} from "../types/communications";

export const generateExplanation = (runId: number | string) =>
  apiFetch<ExplanationContent>(`/underwriting/runs/${runId}/explanation`, {
    method: "POST",
  });

export const generateWhatsAppDraft = (
  runId: number | string,
  messageType: "credit_offer" | "insurance_offer" | "combined_offer" = "combined_offer"
) =>
  apiFetch<ExplanationContent>(`/underwriting/runs/${runId}/whatsapp-draft`, {
    method: "POST",
    body: JSON.stringify({ message_type: messageType }),
  });

export const sendWhatsApp = (
  runId: number | string,
  body: { recipient_phone: string; message_type: string }
) =>
  apiFetch<WhatsAppMessage>(`/underwriting/runs/${runId}/send-whatsapp`, {
    method: "POST",
    body: JSON.stringify(body),
  });

export const getCommunications = (runId: number | string) =>
  apiFetch<CommunicationsResponse>(`/underwriting/runs/${runId}/communications`);
