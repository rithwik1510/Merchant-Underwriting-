export interface ExplanationMetric {
  label: string;
  value: string;
  benchmark_value?: string;
  comparison_text?: string;
}

export interface ExplanationPayload {
  summary?: string;
  rationale_sentences?: string[];
  key_strengths?: string[];
  key_risks?: string[];
  cited_metrics?: ExplanationMetric[];
  message_body?: string;
  cta_text?: string;
  tone_label?: string;
  [key: string]: unknown;
}

export interface ExplanationContent {
  generation_id: number;
  provider_name: string;
  model_name: string;
  generation_type: string;
  status: string;
  output_payload_json: ExplanationPayload;
  validation_errors_json: string[] | null;
  created_at: string;
}

export interface WhatsAppMessage {
  id: number;
  llm_generation_id: number | null;
  recipient_phone: string;
  message_type: string;
  content_text: string;
  twilio_message_sid: string | null;
  delivery_status: string;
  provider_response_json: Record<string, unknown> | null;
  failure_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface CommunicationsResponse {
  latest_explanation: ExplanationContent | null;
  latest_whatsapp_draft: ExplanationContent | null;
  whatsapp_messages: WhatsAppMessage[];
}

export interface LLMProbeResponse {
  provider: string;
  model: string;
  ok: boolean;
  status: string;
  latency_ms: number | null;
  used_override_key: boolean;
  error_detail: string | null;
}
