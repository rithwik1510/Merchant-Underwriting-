export interface ExplanationContent {
  generation_id: number;
  provider_name: string;
  model_name: string;
  generation_type: string;
  status: string;
  output_payload_json: Record<string, unknown>;
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
