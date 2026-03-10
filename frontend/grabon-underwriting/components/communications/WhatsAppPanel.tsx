"use client";

import { useState } from "react";
import { Loader2, MessageSquareText, RefreshCw, Send } from "lucide-react";
import { ExplanationContent, WhatsAppMessage } from "@/lib/types/communications";
import { generateWhatsAppDraft, sendWhatsApp } from "@/lib/api/communications";
import { ApiError } from "@/lib/api/client";
import { formatDate, formatRelativeTime } from "@/lib/utils/formatters";

interface WhatsAppPanelProps {
  runId: number;
  initialDraft?: ExplanationContent | null;
  initialMessages?: WhatsAppMessage[];
}

function extractDraftText(content: ExplanationContent) {
  const payload = content.output_payload_json;
  if (typeof payload === "string") return payload;
  if (payload?.message_body) return String(payload.message_body);
  if (payload?.message) return String(payload.message);
  if (payload?.whatsapp_message) return String(payload.whatsapp_message);
  if (payload?.text) return String(payload.text);
  return JSON.stringify(payload, null, 2);
}

const STATUS_TONE: Record<string, string> = {
  draft: "border-violet-200 bg-violet-50 text-violet-700",
  queued: "border-sky-200 bg-sky-50 text-sky-700",
  sent: "border-go-200 bg-go-50 text-go-700",
  delivered: "border-go-200 bg-go-50 text-go-700",
  failed: "border-risk-200 bg-risk-50 text-risk-700",
};

export function WhatsAppPanel({
  runId,
  initialDraft,
  initialMessages = [],
}: WhatsAppPanelProps) {
  const [draft, setDraft] = useState<ExplanationContent | null>(initialDraft ?? null);
  const [messages, setMessages] = useState<WhatsAppMessage[]>(initialMessages);
  const [draftLoading, setDraftLoading] = useState(false);
  const [sendLoading, setSendLoading] = useState(false);
  const [phone, setPhone] = useState("whatsapp:+91");
  const [error, setError] = useState<string | null>(null);
  const [sendSuccess, setSendSuccess] = useState(false);

  async function handleGenerateDraft() {
    setDraftLoading(true);
    setError(null);
    try {
      const result = await generateWhatsAppDraft(runId);
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
        message_type: "combined_offer",
      });
      setMessages((prev) => [message, ...prev]);
      setPhone(normalizedPhone);
      setSendSuccess(true);
      setTimeout(() => setSendSuccess(false), 2800);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Message send failed");
    } finally {
      setSendLoading(false);
    }
  }

  const draftText = draft ? extractDraftText(draft) : null;

  return (
    <div className="space-y-4">
      <div className="panel-card overflow-hidden">
        <div className="flex items-center justify-between border-b border-ink-100 px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-sky-200 bg-sky-50">
              <MessageSquareText className="h-4 w-4 text-sky-700" />
            </div>
            <div>
              <div className="text-sm font-semibold text-ink-900">WhatsApp draft</div>
              <div className="text-sm text-ink-500">
                Create and review merchant-facing outbound copy
              </div>
            </div>
          </div>

          <button onClick={handleGenerateDraft} disabled={draftLoading} className="btn-outline">
            {draftLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            {draft ? "Regenerate" : "Generate"}
          </button>
        </div>

        <div className="space-y-4 p-5">
          {!draft && !draftLoading ? (
            <div className="rounded-2xl border border-ink-100 bg-surface-50 px-4 py-5 text-sm text-ink-500">
              Generate a WhatsApp-ready draft using the final underwriting outputs and validated explanation layer.
            </div>
          ) : null}

          {draftLoading ? (
            <div className="rounded-2xl border border-sky-200 bg-sky-50 px-4 py-4 text-sm text-sky-700">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Building merchant-facing message draft...
              </div>
            </div>
          ) : null}

          {draftText ? (
            <div className="rounded-[28px] border border-ink-100 bg-surface-50 p-4">
              <div className="mx-auto max-w-md rounded-[28px] border border-ink-100 bg-white p-3 shadow-card">
                <div className="rounded-[22px] rounded-tr-md bg-[linear-gradient(135deg,#0f4ae6,#1d63ff)] px-4 py-4 text-sm leading-6 text-white">
                  {draftText}
                </div>
                <div className="mt-2 text-right text-[11px] text-ink-400">
                  {draft ? formatDate(draft.created_at) : ""}
                </div>
              </div>
            </div>
          ) : null}

          {draft ? (
            <div className="rounded-2xl border border-ink-100 bg-white p-4">
              <div className="mb-3 text-sm font-semibold text-ink-900">Send via Twilio sandbox</div>
              <div className="flex flex-col gap-3 sm:flex-row">
                <input
                  type="tel"
                  value={phone}
                  onChange={(event) => setPhone(event.target.value)}
                  placeholder="whatsapp:+91XXXXXXXXXX"
                  className="flex-1 rounded-xl border border-ink-200 bg-white px-3 py-2.5 font-mono text-sm text-ink-900 placeholder:text-ink-300 focus:border-go-500 focus:outline-none"
                />
                <button onClick={handleSend} disabled={sendLoading || sendSuccess} className="btn-primary">
                  {sendLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  {sendSuccess ? "Sent" : "Send"}
                </button>
              </div>
              <p className="mt-2 text-xs text-ink-400">
                Use the joined sandbox number in Twilio format, for example{" "}
                <span className="font-mono">whatsapp:+918096534845</span>.
              </p>
              {error ? <p className="mt-2 text-xs text-risk-600">{error}</p> : null}
            </div>
          ) : null}
        </div>
      </div>

      {messages.length ? (
        <div className="panel-card overflow-hidden">
          <div className="border-b border-ink-100 px-5 py-4">
            <div className="text-sm font-semibold text-ink-900">Communication log</div>
            <div className="mt-1 text-sm text-ink-500">
              Persisted outbound messages and delivery state
            </div>
          </div>

          <div className="divide-y divide-ink-100">
            {messages.map((message) => (
              <div key={message.id} className="flex items-center gap-4 px-5 py-4">
                <div className="min-w-0 flex-1">
                  <div className="font-mono text-sm text-ink-800">{message.recipient_phone}</div>
                  <div className="mt-1 text-sm text-ink-500">
                    {formatRelativeTime(message.created_at)} | {message.message_type.replace(/_/g, " ")}
                  </div>
                </div>
                <span
                  className={`status-pill ${
                    STATUS_TONE[message.delivery_status] ?? "border-ink-200 bg-surface-100 text-ink-500"
                  }`}
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

function normalizeWhatsAppPhone(value: string) {
  const trimmed = value.trim();
  if (!trimmed) return "";
  if (trimmed.startsWith("whatsapp:+")) return trimmed;
  if (trimmed.startsWith("+")) return `whatsapp:${trimmed}`;
  return trimmed.startsWith("whatsapp:") ? trimmed : `whatsapp:${trimmed}`;
}
