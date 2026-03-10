"use client";

import { useMemo, useState } from "react";
import { BrainCircuit, CheckCircle2, Loader2, MessageSquareText, RefreshCw, Send } from "lucide-react";
import { ApiError } from "@/lib/api/client";
import { generateExplanation, generateWhatsAppDraft, sendWhatsApp } from "@/lib/api/communications";
import { ExplanationContent, WhatsAppMessage } from "@/lib/types/communications";
import { cn } from "@/lib/utils";
import { formatDate, formatRelativeTime } from "@/lib/utils/formatters";

type MessageType = "credit_offer" | "insurance_offer" | "combined_offer";

interface CommunicationWorkspaceProps {
  runId: number;
  initialExplanation?: ExplanationContent | null;
  initialDraft?: ExplanationContent | null;
  initialMessages?: WhatsAppMessage[];
}

const MESSAGE_OPTIONS: { value: MessageType; label: string; description: string }[] = [
  { value: "credit_offer", label: "Credit", description: "Credit message" },
  { value: "insurance_offer", label: "Insurance", description: "Insurance message" },
  { value: "combined_offer", label: "Combined", description: "Combined message" },
];

const STATUS_TONE: Record<string, string> = {
  draft: "border-go-200 bg-go-50 text-go-700",
  queued: "border-go-200 bg-go-50 text-go-700",
  sent: "border-go-200 bg-go-50 text-go-700",
  delivered: "border-go-200 bg-go-50 text-go-700",
  failed: "border-risk-200 bg-risk-50 text-risk-700",
};

function extractText(content: ExplanationContent) {
  const payload = content.output_payload_json;
  if (typeof payload === "string") return payload;
  if (payload?.summary) return String(payload.summary);
  if (payload?.explanation) return String(payload.explanation);
  if (payload?.text) return String(payload.text);
  return JSON.stringify(payload, null, 2);
}

function extractDraft(content: ExplanationContent) {
  const payload = content.output_payload_json;
  if (typeof payload === "string") return payload;
  if (payload?.message_body) return String(payload.message_body);
  if (payload?.message) return String(payload.message);
  if (payload?.whatsapp_message) return String(payload.whatsapp_message);
  if (payload?.text) return String(payload.text);
  return JSON.stringify(payload, null, 2);
}

function normalizeWhatsAppPhone(value: string) {
  const trimmed = value.trim();
  if (!trimmed) return "";
  if (trimmed.startsWith("whatsapp:+")) return trimmed;
  if (trimmed.startsWith("+")) return `whatsapp:${trimmed}`;
  return trimmed.startsWith("whatsapp:") ? trimmed : `whatsapp:${trimmed}`;
}

export function CommunicationWorkspace({
  runId,
  initialExplanation = null,
  initialDraft = null,
  initialMessages = [],
}: CommunicationWorkspaceProps) {
  const [messageType, setMessageType] = useState<MessageType>("combined_offer");
  const [explanation, setExplanation] = useState<ExplanationContent | null>(initialExplanation);
  const [draft, setDraft] = useState<ExplanationContent | null>(initialDraft);
  const [messages, setMessages] = useState<WhatsAppMessage[]>(initialMessages);
  const [phone, setPhone] = useState("whatsapp:+91");
  const [explanationLoading, setExplanationLoading] = useState(false);
  const [draftLoading, setDraftLoading] = useState(false);
  const [sendLoading, setSendLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sendSuccess, setSendSuccess] = useState(false);

  const selectedMessage = useMemo(
    () => MESSAGE_OPTIONS.find((option) => option.value === messageType) ?? MESSAGE_OPTIONS[2],
    [messageType]
  );

  async function handleGenerateExplanation() {
    setExplanationLoading(true);
    setError(null);
    try {
      const result = await generateExplanation(runId);
      setExplanation(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Explanation generation failed");
    } finally {
      setExplanationLoading(false);
    }
  }

  async function handleGenerateDraft() {
    setDraftLoading(true);
    setError(null);
    try {
      const result = await generateWhatsAppDraft(runId, messageType);
      setDraft(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Draft generation failed");
    } finally {
      setDraftLoading(false);
    }
  }

  async function handleSend() {
    const normalizedPhone = normalizeWhatsAppPhone(phone);
    if (!normalizedPhone || normalizedPhone === "whatsapp:+91") {
      setError("Please enter a valid WhatsApp number");
      return;
    }

    setSendLoading(true);
    setError(null);
    try {
      const message = await sendWhatsApp(runId, {
        recipient_phone: normalizedPhone,
        message_type: messageType,
      });
      setMessages((previous) => [message, ...previous]);
      setPhone(normalizedPhone);
      setSendSuccess(true);
      setTimeout(() => setSendSuccess(false), 2200);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Message send failed");
    } finally {
      setSendLoading(false);
    }
  }

  const explanationText = explanation ? extractText(explanation) : "";
  const draftText = draft ? extractDraft(draft) : "";

  return (
    <div className="space-y-4">
      <div className="panel-card overflow-hidden">
        <div className="border-b border-ink-100 px-5 py-4">
          <div className="space-y-3">
            <div>
              <div className="text-sm font-semibold text-ink-900">Communication workspace</div>
              <p className="mt-1 text-sm text-ink-500">Choose mode, generate, send.</p>
            </div>

            <div className="grid gap-2 md:grid-cols-2">
              {MESSAGE_OPTIONS.slice(0, 2).map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setMessageType(option.value)}
                  className={cn(
                    "rounded-2xl border px-4 py-3 text-left transition-all",
                    messageType === option.value
                      ? option.value === "insurance_offer"
                        ? "border-risk-300 bg-risk-50 shadow-sm"
                        : "border-go-300 bg-go-50 shadow-sm"
                      : option.value === "insurance_offer"
                        ? "border-risk-200/70 bg-surface-card hover:border-risk-300 hover:bg-risk-50/60"
                        : "border-ink-100 bg-surface-card hover:border-go-200 hover:bg-go-50/50"
                  )}
                >
                  <div className="text-sm font-semibold text-ink-900">{option.label}</div>
                  <div className="mt-0.5 text-xs text-ink-500">{option.description}</div>
                </button>
              ))}
            </div>

            <button
              type="button"
              onClick={() => setMessageType("combined_offer")}
              className={cn(
                "w-full rounded-2xl border px-4 py-3 text-left transition-all",
                messageType === "combined_offer"
                  ? "border-go-300 bg-go-50 shadow-sm"
                  : "border-ink-100 bg-surface-card hover:border-go-200 hover:bg-go-50/50"
              )}
            >
              <div className="text-sm font-semibold text-ink-900">{MESSAGE_OPTIONS[2].label}</div>
              <div className="mt-0.5 text-xs text-ink-500">{MESSAGE_OPTIONS[2].description}</div>
            </button>
          </div>
        </div>

        <div className="space-y-4 p-5">
          <div className="grid gap-4 xl:grid-cols-[0.95fr_1.15fr]">
            <div className="space-y-4">
              <div className="rounded-[24px] border border-ink-100 bg-surface-50 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 flex h-10 w-10 items-center justify-center rounded-2xl border border-go-200 bg-surface-card">
                      <BrainCircuit className="h-4 w-4 text-go-700" />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-ink-900">AI summary</div>
                      <div className="mt-1 text-sm text-ink-500">Short grounded summary.</div>
                    </div>
                  </div>
                  <button onClick={handleGenerateExplanation} disabled={explanationLoading} className="btn-outline">
                    {explanationLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                    {explanation ? "Refresh" : "Generate"}
                  </button>
                </div>

                <div className="mt-4 rounded-2xl border border-ink-100 bg-surface-card p-4">
                  {explanationLoading ? (
                    <div className="flex items-center gap-2 text-sm text-go-700">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Generating...
                    </div>
                  ) : explanation && explanationText ? (
                    <div className="space-y-3">
                      <div className="flex flex-wrap gap-2">
                        <span className="status-pill border-go-200 bg-go-50 text-go-700">
                          {explanation.status.replace(/_/g, " ")}
                        </span>
                        <span className="status-pill border-ink-200 bg-surface-50 text-ink-500">
                          {formatDate(explanation.created_at)}
                        </span>
                      </div>
                      <p className="text-sm leading-6 text-ink-700">{explanationText}</p>
                    </div>
                  ) : (
                    <p className="text-sm text-ink-500">Generate summary first.</p>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="rounded-[24px] border border-ink-100 bg-surface-card p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 flex h-10 w-10 items-center justify-center rounded-2xl border border-go-200 bg-surface-card">
                      <MessageSquareText className="h-4 w-4 text-go-700" />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-ink-900">WhatsApp</div>
                      <div className="mt-1 text-sm text-ink-500">{selectedMessage.label} copy.</div>
                    </div>
                  </div>
                  <button onClick={handleGenerateDraft} disabled={draftLoading} className="btn-outline">
                    {draftLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                    {draft ? "Regenerate" : "Generate"}
                  </button>
                </div>

                <div className="mt-4 rounded-[24px] border border-ink-100 bg-surface-50 p-4">
                  {draftLoading ? (
                    <div className="flex items-center gap-2 text-sm text-go-700">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Building draft...
                    </div>
                  ) : draft && draftText ? (
                    <div className="space-y-4">
                      <div className="flex flex-wrap gap-2">
                        <span
                          className={cn(
                            "status-pill",
                            selectedMessage.value === "insurance_offer"
                              ? "border-risk-300 bg-risk-50 text-risk-700"
                              : "border-go-200 bg-go-50 text-go-700"
                          )}
                        >
                          {selectedMessage.label}
                        </span>
                        <span className="status-pill border-ink-200 bg-surface-50 text-ink-500">
                          {formatDate(draft.created_at)}
                        </span>
                      </div>

                      <div className="mx-auto max-w-xl rounded-[28px] border border-ink-100 bg-surface-card p-3">
                        <div className="rounded-[22px] rounded-tr-md bg-[linear-gradient(135deg,#0f4ae6,#1f67ff)] px-4 py-4 text-sm leading-6 text-white shadow-[0_16px_30px_rgba(15,74,230,0.18)]">
                          {draftText}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-ink-500">Generate draft before send.</p>
                  )}
                </div>

                <div className="mt-4 rounded-[24px] border border-ink-100 bg-surface-card p-4">
                  <div className="flex flex-col gap-3 lg:flex-row">
                    <input
                      type="tel"
                      value={phone}
                      onChange={(event) => setPhone(event.target.value)}
                      placeholder="whatsapp:+91XXXXXXXXXX"
                      className="flex-1 rounded-2xl border border-ink-200 bg-surface-card px-4 py-3 font-mono text-sm text-ink-900 placeholder:text-ink-400 focus:border-go-400 focus:outline-none"
                    />
                    <button
                      onClick={handleSend}
                      disabled={sendLoading}
                      className="inline-flex min-w-[220px] items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,#16a34a,#22c55e)] px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_32px_rgba(22,163,74,0.22)] transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-70"
                    >
                      {sendLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : sendSuccess ? <CheckCircle2 className="h-4 w-4" /> : <Send className="h-4 w-4" />}
                      {sendSuccess ? "Sent" : "Send WhatsApp"}
                    </button>
                  </div>
                  <p className="mt-2 text-xs text-ink-400">
                    Format: <span className="font-mono">whatsapp:+918096534845</span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          {error ? (
            <div className="rounded-2xl border border-risk-200 bg-risk-50 px-4 py-3 text-sm text-risk-700">
              {error}
            </div>
          ) : null}
        </div>
      </div>

      {messages.length ? (
        <div className="panel-card overflow-hidden">
          <div className="border-b border-ink-100 px-5 py-4">
            <div className="text-sm font-semibold text-ink-900">Message history</div>
            <div className="mt-1 text-sm text-ink-500">Recent outbound status.</div>
          </div>
          <div className="divide-y divide-ink-100">
            {messages.map((message) => (
              <div key={message.id} className="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center">
                <div className="min-w-0 flex-1">
                  <div className="font-mono text-sm text-ink-800">{message.recipient_phone}</div>
                  <div className="mt-1 text-sm text-ink-500">
                    {formatRelativeTime(message.created_at)} | {message.message_type.replace(/_/g, " ")}
                  </div>
                </div>
                <span
                  className={cn(
                    "status-pill",
                    STATUS_TONE[message.delivery_status] ?? "border-ink-200 bg-surface-100 text-ink-500"
                  )}
                >
                  {message.delivery_status}
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
